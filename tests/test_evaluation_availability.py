from assistant_mlops.gate import gate
from assistant_mlops.harness import assess
from assistant_mlops.schemas import EvalCase


def test_expected_abstention_still_records_provider_outage():
    case = EvalCase(
        id="outage",
        category="unanswerable",
        question="Unknown?",
        expected_status="abstain",
        reference="Unknown",
        max_steps=7,
    )
    trace = {
        "answer": {"status": "abstain", "answer": "Unknown", "sources": []},
        "termination": "provider_unavailable",
        "steps": [],
        "tool_errors": 0,
        "iterations": 1,
        "tokens": 0,
        "usage_complete": False,
        "latency_seconds": 0.1,
    }
    row = assess(case, trace)
    assert row["completed"]  # Status correctness remains separate from availability.
    assert row["failure_class"] == "hard_failure"


def test_golden_provider_outage_blocks_otherwise_passing_candidate():
    candidate = {
        "calibration_review_approved": 1,
        "pct_ground_truth_passed": 1,
        "pct_judge_passed": 1,
        "judge_label_agreement": 1,
        "judge_truth_agreement": 1,
        "tool_call_correctness": 1,
        "hard_failure_rate": 0,
        "failure_injection_safe": 1,
        "usage_complete": 1,
        "golden_provider_failure_rate": 0.2,
    }
    verdict = gate(candidate)
    assert verdict["verdict"] == "REJECT"
    assert not verdict["checks"]["golden_provider_available"]
