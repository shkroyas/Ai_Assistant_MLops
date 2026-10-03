import pytest

from assistant_mlops.rag import answer_once
from assistant_mlops.retrieval import Corpus
from test_agent import ScriptedProvider, final


@pytest.mark.asyncio
async def test_single_pass_baseline():
    corpus = Corpus()
    provider = ScriptedProvider(
        [
            final(
                "answered",
                "Keys belong in a local .env.",
                [{"source_id": "security", "quote": "local git-ignored .env file"}],
            )
        ]
    )
    result = await answer_once("Where should API keys be stored?", corpus, provider)
    assert result["status"] == "answered" and result["mode"] == "single_pass"
    assert result["tokens"] == 10
    corpus.client.close()
