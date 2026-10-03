import pandas as pd
import pytest
from evidently.core.datasets import ColumnType, DatasetColumn
from evidently.descriptors.llm_judges import LLMEval
from evidently.llm.utils.wrapper import GeminiOptions

from assistant_mlops.regression import deterministic_report, judge, judge_descriptors


def test_native_judge_report_plumbing_with_stubbed_descriptor(monkeypatch, tmp_path):
    """Tests native report/test wiring; explicitly not evidence of judge quality."""
    monkeypatch.setenv("JUDGE_API_KEY", "test-fixture-only")
    monkeypatch.setenv("JUDGE_PROVIDER", "gemini")
    monkeypatch.setenv("JUDGE_REQUEST_INTERVAL_SECONDS", "15")
    pauses = []
    monkeypatch.setattr("assistant_mlops.regression.time.sleep", pauses.append)

    def generate(self, dataset, options):
        assert options.get(GeminiOptions).limits.rpm == 1
        assert options.get(GeminiOptions).limits.interval.total_seconds() >= 15
        return {
            self.alias: DatasetColumn(ColumnType.Categorical, pd.Series(["correct", "incorrect"])),
            self.alias + " reasoning": DatasetColumn(
                ColumnType.Text, pd.Series(["fixture agrees", "fixture disagrees"])
            ),
        }

    monkeypatch.setattr(LLMEval, "generate_data", generate)
    frame = pd.DataFrame(
        {"query": ["one", "two"], "reference": ["yes", "no"], "response": ["yes", "wrong"]}
    )
    scored = judge(frame, tmp_path)
    assert scored.judge_pass.tolist() == [True, False]
    assert (tmp_path / "evidently_judge.html").stat().st_size > 10000
    assert {d.alias for d in judge_descriptors()} == {"correctness", "completeness"}
    assert pauses == [15]


def test_judge_sdk_exception_does_not_expose_key_url(monkeypatch, tmp_path):
    monkeypatch.setenv("JUDGE_API_KEY", "fixture-secret")

    def generate(self, dataset, options):
        raise ValueError("https://fixture.test/generate?key=fixture-secret")

    monkeypatch.setattr(LLMEval, "generate_data", generate)
    frame = pd.DataFrame({"query": ["q"], "reference": ["r"], "response": ["a"]})
    with pytest.raises(RuntimeError) as caught:
        judge(frame, tmp_path)
    assert str(caught.value) == "Judge request failed: ValueError"
    assert caught.value.__suppress_context__


def test_judge_cannot_silently_fake_results(monkeypatch, tmp_path):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("JUDGE_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="requires"):
        judge(pd.DataFrame(), tmp_path)


def test_ground_truth_report_uses_native_tests(tmp_path):
    result = deterministic_report([{"completed": True}, {"completed": False}], tmp_path)
    assert result == 0.5
    assert "FAIL" in (tmp_path / "evidently_ground_truth.json").read_text()
