import argparse
import json
from pathlib import Path

import httpx

parser = argparse.ArgumentParser()
parser.add_argument("--base-url", default="http://localhost:8000")
parser.add_argument("--ui-url", default="http://localhost:8501")
args = parser.parse_args()
health = httpx.get(args.base_url + "/health", timeout=10)
health.raise_for_status()
ui = httpx.get(args.ui_url + "/_stcore/health", timeout=10)
ui.raise_for_status()
payload = {"question": "What happens after drift and what permits promotion?"}
answer = httpx.post(args.base_url + "/ask", json=payload, timeout=910)
answer.raise_for_status()
assert answer.json()["status"] in {"answered", "abstain", "clarify"}
if not health.json()["live_provider_configured"]:
    assert answer.json()["status"] == "abstain"
    assert answer.json()["termination"] == "provider_unavailable"
record = {
    "health": health.json(),
    "ui_status": ui.status_code,
    "ui_url": args.ui_url,
    "request": payload,
    "response": answer.json(),
    "scope": "Deployment and graceful-degradation smoke test, not live model quality",
}
Path("reports/deployment_smoke.json").write_text(json.dumps(record, indent=2))
print(json.dumps(record, indent=2))
