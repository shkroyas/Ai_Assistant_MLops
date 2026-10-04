import sys
from types import SimpleNamespace

import numpy as np
import pytest

from assistant_mlops.retrieval import Corpus


@pytest.mark.parametrize("revision", [None, "main"])
def test_semantic_model_requires_immutable_revision_before_loading(revision):
    with pytest.raises(ValueError, match="pinned"):
        Corpus(embedding_model="public/model", embedding_revision=revision)


def test_persistent_vectors_are_isolated_between_model_revisions(monkeypatch, tmp_path):
    class Encoder:
        def __init__(self, name, **kwargs):
            assert kwargs["trust_remote_code"] is False and kwargs["token"] is False
            self.dimension = 2 if kwargs["revision"] == "a" * 40 else 3

        def get_sentence_embedding_dimension(self):
            return self.dimension

        def encode(self, text, normalize_embeddings):
            assert normalize_embeddings
            return np.ones(self.dimension) / np.sqrt(self.dimension)

    monkeypatch.setitem(
        sys.modules, "sentence_transformers", SimpleNamespace(SentenceTransformer=Encoder)
    )
    folder = tmp_path / "corpus"
    folder.mkdir()
    (folder / "policy.md").write_text("A grounded factual policy.")
    first = Corpus(
        folder,
        path=str(tmp_path / "vectors"),
        embedding_model="public/model",
        embedding_revision="a" * 40,
    )
    fingerprint = first.fingerprint
    assert first.search("policy")[0]["source_id"] == "policy"
    first.client.close()
    second = Corpus(
        folder,
        path=str(tmp_path / "vectors"),
        embedding_model="public/model",
        embedding_revision="b" * 40,
    )
    try:
        assert second.fingerprint != fingerprint
        assert second.search("policy")[0]["source_id"] == "policy"
    finally:
        second.client.close()
