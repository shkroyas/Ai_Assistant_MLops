from fastapi.testclient import TestClient

from assistant_mlops.api import app


def test_cache_singleflight_batch_and_rate_limit(monkeypatch):
    calls = []
    with TestClient(app) as client:

        async def run(question):
            calls.append(question)
            return {
                "query_id": "fixture-only",
                "answer": {"status": "clarify", "answer": "Which model?", "sources": []},
                "iterations": 1,
                "tokens": 10,
                "token_accounting": "provider_usage",
                "termination": "clarify",
            }

        monkeypatch.setattr(app.state.agent, "run", run)
        response = client.post("/batch", json={"questions": [{"question": "Which model?"}] * 2})
        assert response.status_code == 200 and len(calls) == 1
        cached = client.post("/ask", json={"question": "Which model?"}).json()
        assert cached["cache_hit"] and cached["tokens_consumed_this_request"] == 0
        assert client.post("/batch", json={"questions": []}).status_code == 422
        for _ in range(27):
            assert client.post("/ask", json={"question": "Which model?"}).status_code == 200
        assert client.post("/ask", json={"question": "Which model?"}).status_code == 429
