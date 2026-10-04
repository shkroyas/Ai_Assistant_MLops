from fastapi.testclient import TestClient

from assistant_mlops.api import app


def test_unset_override_selects_promoted_config(monkeypatch, tmp_path):
    from assistant_mlops.api import selected_config_path

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ASSISTANT_CONFIG", "")
    (tmp_path / "configs").mkdir()
    production = tmp_path / "configs/production.yaml"
    production.write_text("version: v16\nrun_id: actual-promoted-run\n")
    assert selected_config_path() == "configs/v16.yaml"
    production.write_text("version: v16\nrun_id: null\n")
    assert selected_config_path() == "configs/v1.yaml"


def test_explicit_config_override_takes_precedence(monkeypatch, tmp_path):
    from assistant_mlops.api import selected_config_path

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ASSISTANT_CONFIG", "configs/v4.yaml")
    assert selected_config_path() == "configs/v4.yaml"


def test_rag_uses_groq_baseline_without_proxy_headers(monkeypatch):
    monkeypatch.setenv("ASSISTANT_CONFIG", "configs/v1.yaml")
    monkeypatch.setenv("GROQ_API_KEY", "groq-fixture")
    monkeypatch.setenv("AGENT_PROXY_TOKEN", "proxy-fixture")
    monkeypatch.setenv("AGENT_PROXY_COOKIE", "proxy=session")

    async def answer_once(question, corpus, provider, top_k):
        assert provider.base_url == "https://api.groq.com/openai/v1"
        assert provider.headers["Authorization"] == "Bearer groq-fixture"
        assert "Cookie" not in provider.headers
        return {"status": "clarify", "answer": "Which policy?", "sources": []}

    monkeypatch.setattr("assistant_mlops.api.answer_once", answer_once)
    with TestClient(app) as client:
        assert client.post("/rag", json={"question": "Which policy?"}).status_code == 200
        assert app.state.baseline_provider is not app.state.agent.provider


def test_cache_singleflight_batch_and_rate_limit(monkeypatch):
    monkeypatch.setenv("ASSISTANT_CONFIG", "configs/v1.yaml")
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


def test_paced_agent_has_bounded_deadline_and_recorded_model(monkeypatch, tmp_path):
    import yaml
    from pathlib import Path

    config = yaml.safe_load(Path("configs/v1.yaml").read_text())
    config.update(provider="groq", model="candidate", request_interval_seconds=15)
    path = tmp_path / "paced.yaml"
    path.write_text(yaml.safe_dump(config))
    monkeypatch.setenv("ASSISTANT_CONFIG", str(path))
    monkeypatch.setenv("GROQ_API_KEY", "groq-fixture")
    with TestClient(app) as client:
        health = client.get("/health").json()
        assert health["provider_model"] == "candidate"
        assert 7 * 4 * 15 < health["query_timeout_seconds"] <= 900
