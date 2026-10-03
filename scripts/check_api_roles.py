"""Small live role checks; neither a benchmark nor human judge calibration."""

import asyncio
import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from assistant_mlops.agent import TOOLS
from assistant_mlops.provider import ChatProvider
from assistant_mlops.rag import answer_once
from assistant_mlops.regression import judge
from assistant_mlops.retrieval import Corpus


async def check():
    load_dotenv()
    record = {"scope": "Live provider-role smoke checks, not full evaluation or calibration"}
    provider = ChatProvider(
        base_url="https://api.groq.com/openai/v1",
        key=os.environ["GROQ_API_KEY"],
        model="openai/gpt-oss-20b",
        auth_prefix="GROQ",
    )
    provider.fallback_url = None
    corpus = Corpus()
    try:
        record["groq_baseline"] = await answer_once(
            "How many provider attempts and what retry strategy are allowed?", corpus, provider
        )
        message, usage = await provider.complete(
            [{"role": "user", "content": "Search for the drift policy using the search tool."}],
            TOOLS,
        )
        record["groq_native_tools"] = message.get("tool_calls") or []
        record["groq_usage"] = usage
        rows = [
            {
                "query": "How many provider attempts and what retry strategy are allowed?",
                "reference": "Retry up to three attempts with exponential backoff.",
                "response": response,
            }
            for response in [
                "Retry up to three attempts with exponential backoff.",
                "Retry forever without backoff.",
            ]
        ]
        scored = await asyncio.to_thread(judge, pd.DataFrame(rows), "reports/provider_judge_smoke")
        record["gemini_judge_verdicts"] = [bool(value) for value in scored.judge_pass]
        record["passed"] = (
            record["groq_baseline"]["status"] == "answered"
            and bool(record["groq_native_tools"])
            and record["gemini_judge_verdicts"] == [True, False]
        )
    except Exception as exc:
        # SDK error text may contain credential-bearing URLs; retain only the class.
        record["error_type"] = type(exc).__name__
        record["passed"] = False
    finally:
        await provider.close()
        corpus.client.close()
    return record


if __name__ == "__main__":
    result = asyncio.run(check())
    Path("reports/provider_roles_smoke.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
