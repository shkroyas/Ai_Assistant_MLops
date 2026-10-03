"""Record live caching, shared concurrent computation, and batch API evidence."""

import argparse
import asyncio
import json
from pathlib import Path
from time import perf_counter

import httpx


async def main(base_url):
    async with httpx.AsyncClient(base_url=base_url, timeout=910) as client:
        health = await client.get("/health")
        health.raise_for_status()

        async def ask(question):
            response = await client.post("/ask", json={"question": question})
            response.raise_for_status()
            return response.json()

        question = "How long are cached responses kept?"
        started = perf_counter()
        concurrent = await asyncio.gather(ask(question), ask(question))
        duration = perf_counter() - started
        cached = await ask(question)
        response = await client.post(
            "/batch",
            json={
                "questions": [
                    {"question": question},
                    {"question": "How many concurrent model requests can the application admit?"},
                ]
            },
        )
        response.raise_for_status()
        batch = response.json()
        checks = {
            "live_grounded_answers": all(
                answer["status"] == "answered"
                and answer["sources"]
                and answer["token_accounting"] == "provider_usage"
                for answer in concurrent + batch
            ),
            "shared_query_id": concurrent[0]["query_id"] == concurrent[1]["query_id"],
            "single_new_computation": sum(
                answer["tokens_consumed_this_request"] > 0 for answer in concurrent
            )
            == 1,
            "cache_reuse": cached["cache_hit"] and cached["tokens_consumed_this_request"] == 0,
            "batch_size": len(batch) == 2,
            "batch_cached_answer": batch[0]["cache_hit"],
        }
        Path("reports/api_features_smoke.json").write_text(
            json.dumps(
                {
                    "health": health.json(),
                    "question": question,
                    "concurrent": concurrent,
                    "concurrent_wall_seconds": duration,
                    "cached": cached,
                    "batch": batch,
                    "checks": checks,
                    "passed": all(checks.values()),
                },
                indent=2,
            )
        )
        print(json.dumps(checks, indent=2))
        return all(checks.values())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    raise SystemExit(0 if asyncio.run(main(parser.parse_args().base_url)) else 1)
