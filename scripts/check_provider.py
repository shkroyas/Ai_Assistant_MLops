"""Check the configured endpoint without logging credentials or upstream error bodies."""

import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx
import yaml
from dotenv import load_dotenv

from assistant_mlops.agent import TOOLS
from assistant_mlops.provider import ChatProvider, provider_for_config


async def check(config_path=None):
    load_dotenv()
    config = yaml.safe_load(config_path.read_text()) if config_path else None
    provider = provider_for_config(config) if config else ChatProvider()
    # Verify the selected endpoint itself; fallback success cannot prove GPU access.
    provider.fallback_url = None
    record = {"checked_at": datetime.now(timezone.utc).isoformat(), "model": provider.model}
    if config:
        record["configuration_version"] = config["version"]
        record["enable_thinking"] = config.get("enable_thinking")
    try:
        response = await provider.client.get(
            provider.base_url.rstrip("/") + "/models", headers=provider.headers
        )
        record["models_http_status"] = response.status_code
        if response.status_code != 200:
            record["status"] = (
                "authentication_failed"
                if response.status_code in {401, 403}
                else "endpoint_unavailable"
            )
            return record
        record["model_listed"] = provider.model in {item["id"] for item in response.json()["data"]}
        if not record["model_listed"]:
            record["status"] = "configured_model_missing"
            return record
        message, usage = await provider.complete(
            [{"role": "user", "content": "Say hello in Nepali"}], []
        )
        record["greeting"] = message.get("content")
        record["greeting_usage"] = usage
        message, usage = await provider.complete(
            [
                {
                    "role": "user",
                    "content": "Use the search tool to find the drift policy. Do not answer without searching.",
                }
            ],
            TOOLS,
        )
        record["native_tool_calls"] = message.get("tool_calls") or []
        record["tool_usage"] = usage
        valid_tools = {tool["function"]["name"] for tool in TOOLS}
        calls = record["native_tool_calls"]
        record["status"] = (
            "passed"
            if calls and all(call["function"]["name"] in valid_tools for call in calls)
            else "tool_call_missing_or_invalid"
        )
    except (httpx.RequestError, RuntimeError, ValueError, KeyError) as exc:
        record["status"] = "connection_or_provider_failed"
        record["error_type"] = type(exc).__name__
    finally:
        await provider.close()
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("reports/provider_connection.json"))
    parser.add_argument("--config", type=Path)
    args = parser.parse_args()
    result = asyncio.run(check(args.config))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "passed" else 1)
