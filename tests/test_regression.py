import pandas as pd
import pytest
from evidently.core.datasets import ColumnType, DatasetColumn
from evidently.descriptors.llm_judges import LLMEval

from assistant_mlops.regression import deterministic_report, judge, judge_descriptors


def test_native_judge_report_plumbing_with_stubbed_descriptor(monkeypatch, tmp_path):
    """Tests native report/test wiring; explicitly not evidence of judge quality."""
    monkeypatch.setenv("JUDGE_API_KEY", "test-fixture-only")

    def generate(self, dataset, options):
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


def test_judge_cannot_silently_fake_results(monkeypatch, tmp_path):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("JUDGE_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="requires"):
        judge(pd.DataFrame(), tmp_path)


def test_ground_truth_report_uses_native_tests(tmp_path):
    result = deterministic_report([{"completed": True}, {"completed": False}], tmp_path)
    assert result == 0.5
    assert "FAIL" in (tmp_path / "evidently_ground_truth.json").read_text()
