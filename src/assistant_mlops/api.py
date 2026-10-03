import asyncio
import copy
import hashlib
import json
import os
import time
from collections import OrderedDict, defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path

import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from assistant_mlops.agent import Agent
from assistant_mlops.provider import ChatProvider, provider_for_config
from assistant_mlops.retrieval import Corpus
from assistant_mlops.rag import answer_once
from assistant_mlops.schemas import Query

load_dotenv()


class Batch(BaseModel):
    questions: list[Query] = Field(min_length=1, max_length=8)


def selected_config_path():
    selected = os.getenv("ASSISTANT_CONFIG")
    if not selected:
        production = yaml.safe_load(Path("configs/production.yaml").read_text())
        selected = (
            f"configs/{production['version']}.yaml"
            if production.get("run_id")
            else "configs/v1.yaml"
        )
    return selected


@asynccontextmanager
async def lifespan(app):
    selected = selected_config_path()
    config = yaml.safe_load(Path(selected).read_text())
    corpus = Corpus(path=os.getenv("QDRANT_PATH") or None)
    provider = provider_for_config(config)
    app.state.agent = Agent(corpus, provider, config)
    app.state.query_timeout = min(
        900, max(180, 4 * config["max_iterations"] * provider.request_interval_seconds + 40)
    )
    app.state.baseline_provider = provider
    if os.getenv("GROQ_API_KEY"):
        app.state.baseline_provider = ChatProvider(
            base_url="https://api.groq.com/openai/v1",
            key=os.environ["GROQ_API_KEY"],
            model=os.getenv("GROQ_MODEL") or "openai/gpt-oss-20b",
            auth_prefix="GROQ",
        )
        app.state.baseline_provider.fallback_url = None
    app.state.semaphore = asyncio.Semaphore(4)
    app.state.cache = OrderedDict()
    app.state.inflight = {}
    app.state.cache_lock = asyncio.Lock()
    app.state.clients = defaultdict(deque)
    app.state.fingerprint = hashlib.sha256(
        (
            json.dumps(config, sort_keys=True)
            + corpus.fingerprint
            + app.state.agent.prompt
            + provider.model
            + provider.base_url
        ).encode()
    ).hexdigest()
    yield
    if app.state.baseline_provider is not provider:
        await app.state.baseline_provider.close()
    await provider.close()
    corpus.client.close()


app = FastAPI(title="MLOps Knowledge Assistant", lifespan=lifespan)


def admit(request, cost=1):
    now = time.monotonic()
    host = request.client.host if request.client else "local"
    clients = request.app.state.clients
    # Expire inactive entries rather than retaining an unbounded map of visitors.
    for key in list(clients):
        while clients[key] and clients[key][0] <= now - 60:
            clients[key].popleft()
        if not clients[key]:
            del clients[key]
    window = clients[host]
    if len(window) + cost > 30:
        raise HTTPException(429, "30 queries per minute per client", headers={"Retry-After": "60"})
    window.extend([now] * cost)


async def compute(question):
    async with app.state.semaphore:
        return await asyncio.wait_for(
            app.state.agent.run(question), timeout=app.state.query_timeout
        )


async def answer(question):
    key = (app.state.fingerprint, question)
    async with app.state.cache_lock:
        cached = app.state.cache.get(key)
        if cached and time.monotonic() - cached[0] < 300:
            result = copy.deepcopy(cached[1])
            result["cache_hit"] = True
            result["tokens_consumed_this_request"] = 0
            return result
        task = app.state.inflight.get(key)
        created = task is None
        if created:
            task = asyncio.create_task(compute(question))
            app.state.inflight[key] = task
    try:
        trace = await asyncio.shield(task)
    except asyncio.TimeoutError:
        raise HTTPException(504, "Request exceeded the bounded execution timeout") from None
    finally:
        async with app.state.cache_lock:
            if task.done():
                app.state.inflight.pop(key, None)
    result = {
        **trace["answer"],
        "query_id": trace["query_id"],
        "iterations": trace["iterations"],
        "tokens": trace["tokens"],
        "token_accounting": trace["token_accounting"],
        "tokens_consumed_this_request": trace["tokens"] if created else 0,
        "shared_computation": not created,
        "cache_hit": False,
        "termination": trace["termination"],
    }
    async with app.state.cache_lock:
        # Infrastructure errors must not poison the answer cache.
        if trace["termination"] in {"answered", "clarify"}:
            app.state.cache[key] = (time.monotonic(), copy.deepcopy(result))
            app.state.cache.move_to_end(key)
            while len(app.state.cache) > 128:
                app.state.cache.popitem(last=False)
    return result


@app.get("/health")
def health():
    return {
        "status": "ready",
        "provider_model": app.state.agent.provider.model,
        "query_timeout_seconds": app.state.query_timeout,
        "baseline_model": app.state.baseline_provider.model,
        "live_provider_configured": app.state.agent.provider.configured,
    }


@app.post("/ask")
async def ask(query: Query, request: Request):
    admit(request)
    return await answer(query.question)


@app.post("/batch")
async def batch(queries: Batch, request: Request):
    admit(request, len(queries.questions))
    return await asyncio.gather(*(answer(q.question) for q in queries.questions))


@app.post("/rag")
async def rag(query: Query, request: Request):
    admit(request)
    async with app.state.semaphore:
        return await asyncio.wait_for(
            answer_once(
                query.question,
                app.state.agent.corpus,
                app.state.baseline_provider,
                app.state.agent.config["top_k"],
            ),
            timeout=180,
        )
