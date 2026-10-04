import json
from pathlib import Path

import pytest
import yaml

from assistant_mlops.agent import Agent, parse_final
from assistant_mlops.gate import gate
from assistant_mlops.harness import assess, load_cases
from assistant_mlops.retrieval import Corpus
from assistant_mlops.schemas import EvalCase


class ScriptedProvider:
    """Protocol fixture only. Its results must never be represented as LLM quality evidence."""

    def __init__(self, messages):
        self.messages = iter(messages)

    async def complete(self, *args):
        return next(self.messages), {
            "total_tokens": 10,
            "prompt_tokens": 7,
            "completion_tokens": 3,
            "model": "fixture",
            "fallback": False,
        }


def call(name, args):
    return {
        "content": None,
        "tool_calls": [
            {
                "id": "call-1",
                "type": "function",
                "function": {"name": name, "arguments": json.dumps(args)},
            }
        ],
    }


def final(status, answer, sources=None):
    return {"content": json.dumps({"status": status, "answer": answer, "sources": sources or []})}


@pytest.fixture
def corpus():
    value = Corpus()
    yield value
    value.client.close()


@pytest.mark.asyncio
async def test_bounded_review_preserves_native_protocol_and_charges_all_calls(corpus):
    class ReviewingProvider(ScriptedProvider):
        async def complete(self, messages, *args):
            if messages[-1]["role"] == "tool":
                assert messages[-2]["tool_calls"][0]["id"] == messages[-1]["tool_call_id"]
                assert json.loads(messages[-1]["content"])["review_required"]
            return await super().complete(messages, *args)

    provider = ReviewingProvider(
        [
            call("json", {"status": "clarify", "answer": "Draft question", "sources": []}),
            call(
                "json",
                {"status": "abstain", "answer": "No verified personal record", "sources": []},
            ),
        ]
    )
    config = yaml.safe_load(Path("configs/v15.yaml").read_text())
    config.update(native_final_answer=True, review_final_answer=True)
    trace = await Agent(corpus, provider, config).run("What is my account balance?")
    assert trace["answer"]["status"] == "abstain" and trace["iterations"] == 2
    assert trace["tokens"] == 20 and trace["usage_complete"]
    assert [step["event"] for step in trace["steps"]] == ["draft_answer", "finish"]


@pytest.mark.asyncio
async def test_review_never_accepts_unreviewed_draft_at_iteration_limit(corpus):
    config = yaml.safe_load(Path("configs/v15.yaml").read_text())
    config.update(max_iterations=1, native_final_answer=True, review_final_answer=True)
    provider = ScriptedProvider(
        [
            call("json", {"status": "clarify", "answer": "Draft question", "sources": []}),
        ]
    )
    trace = await Agent(corpus, provider, config).run("Which one?")
    assert trace["termination"] == "max_iterations" and trace["answer"]["status"] == "abstain"
    assert trace["tokens"] == 10 and trace["usage_complete"]


@pytest.mark.asyncio
async def test_answered_only_review_preserves_a_safe_refusal(corpus):
    config = yaml.safe_load(Path("configs/v15.yaml").read_text())
    config.update(native_final_answer=True, review_final_answer=True, review_scope="answered")
    provider = ScriptedProvider(
        [
            call(
                "json", {"status": "abstain", "answer": "Cannot fabricate evidence", "sources": []}
            ),
        ]
    )
    trace = await Agent(corpus, provider, config).run("Invent proof for this claim")
    assert trace["termination"] == "abstain" and trace["iterations"] == 1
    assert trace["tokens"] == 10 and trace["usage_complete"]
    assert not any(step["event"] == "draft_answer" for step in trace["steps"])


@pytest.mark.asyncio
async def test_nullable_search_schema_matches_unfiltered_runtime(corpus):
    class SchemaCheckingProvider(ScriptedProvider):
        async def complete(self, messages, tools, *args):
            assert tools[0]["function"]["parameters"]["properties"]["source_id"]["type"] == [
                "string",
                "null",
            ]
            assert tools[1]["function"]["parameters"]["properties"]["source_id"]["type"] == "string"
            return await super().complete(messages, tools, *args)

    provider = SchemaCheckingProvider(
        [
            call("search", {"query": "retry limit", "source_id": None, "reason": "Find guidance"}),
            final("abstain", "Fixture final; no quality claim"),
        ]
    )
    config = yaml.safe_load(Path("configs/v15.yaml").read_text())
    config["nullable_search_filter"] = True
    trace = await Agent(corpus, provider, config).run("What is the retry limit?")
    assert trace["steps"][0]["valid"]
    assert trace["steps"][0]["result"] == corpus.search("retry limit", top_k=config["top_k"])
    assert trace["tool_errors"] == 0


@pytest.mark.asyncio
async def test_native_final_answer_validates_real_retrieved_quote(corpus):
    hit = corpus.search("retry limit", top_k=3)[0]
    provider = ScriptedProvider(
        [
            call("search", {"query": "retry limit", "reason": "Find handbook guidance"}),
            call(
                "json",
                {
                    "status": "answered",
                    "answer": "Fixture grounded answer",
                    "sources": [{"source_id": hit["source_id"], "quote": hit["text"][:60]}],
                },
            ),
        ]
    )
    config = yaml.safe_load(Path("configs/v15.yaml").read_text())
    config["native_final_answer"] = True
    trace = await Agent(corpus, provider, config).run("What is the retry limit?")
    assert trace["termination"] == "answered" and trace["iterations"] == 2
    assert trace["steps"][-1]["native_final_answer"]
    assert trace["steps"][-1]["raw_response"]["tool_calls"][0]["function"]["name"] == "json"


@pytest.mark.asyncio
async def test_native_final_rejects_fabricated_evidence_and_repairs_protocol(corpus):
    class ProtocolCheckingProvider(ScriptedProvider):
        async def complete(self, messages, *args):
            if len(messages) > 2:
                assert messages[-3]["role"] == "assistant"
                assert messages[-3]["tool_calls"][0]["id"] == "call-1"
                assert messages[-2]["role"] == "tool"
                assert messages[-2]["tool_call_id"] == "call-1"
                assert "Citation not present" in messages[-2]["content"]
            return await super().complete(messages, *args)

    provider = ProtocolCheckingProvider(
        [
            call(
                "json",
                {
                    "status": "answered",
                    "answer": "Unverified fixture claim",
                    "sources": [{"source_id": "security", "quote": "Invented quotation"}],
                },
            ),
            call("json", {"status": "abstain", "answer": "Evidence is unavailable", "sources": []}),
        ]
    )
    config = yaml.safe_load(Path("configs/v15.yaml").read_text())
    config["native_final_answer"] = True
    trace = await Agent(corpus, provider, config).run("What is the retry limit?")
    assert trace["answer"]["status"] == "abstain"
    assert trace["steps"][0]["event"] == "invalid_answer"


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["timeout", "malformed", "unavailable"])
async def test_fail_fast_retrieval_never_requests_another_completion(corpus, failure):
    # A second model call would exhaust this fixture and fail the test.
    provider = ScriptedProvider(
        [call("search", {"query": "retry limit", "reason": "Find handbook guidance"})]
    )
    config = yaml.safe_load(Path("configs/v14.yaml").read_text())
    config["stop_on_tool_error"] = True
    trace = await Agent(corpus, provider, config).run("What is the retry limit?", failure=failure)
    assert trace["termination"] == "retrieval_failure"
    assert trace["answer"]["status"] == "abstain"
    assert trace["answer"]["sources"] == []
    assert trace["iterations"] == 1 and trace["tokens"] == 10
    assert trace["tool_errors"] == 1 and trace["usage_complete"]


@pytest.mark.asyncio
async def test_cross_source_loop_and_usage(corpus):
    messages = [
        call(
            "search",
            {
                "query": "drift triggers challenger",
                "source_id": "drift-runbook",
                "reason": "Check drift action",
            },
        ),
        call("read_source", {"source_id": "release-policy", "reason": "Check promotion gate"}),
        final(
            "answered",
            "Drift triggers challenger evaluation. F1 must improve by 0.005.",
            [
                {
                    "source_id": "drift-runbook",
                    "quote": "Drift triggers challenger training and evaluation",
                },
                {"source_id": "release-policy", "quote": "F1 improves by at least 0.005"},
            ],
        ),
    ]
    config = yaml.safe_load(Path("configs/v1.yaml").read_text())
    trace = await Agent(corpus, ScriptedProvider(messages), config).run("What happens after drift?")
    assert trace["answer"]["status"] == "answered"
    assert trace["iterations"] == 3 and trace["tokens"] == 30
    assert trace["steps"][0]["reasoning"] == "Check drift action"
    assert trace["steps"][0]["args"]["reason"] == "Check drift action"


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["timeout", "malformed", "unavailable"])
async def test_failure_injection_recognized(corpus, failure):
    messages = [
        call("search", {"query": "retry limit", "reason": "Find policy"}),
        final("abstain", "Tool failed; cannot verify evidence."),
    ]
    config = yaml.safe_load(Path("configs/v1.yaml").read_text())
    trace = await Agent(corpus, ScriptedProvider(messages), config).run("Retry?", failure)
    assert trace["answer"]["status"] == "abstain"
    assert trace["tool_errors"] == 1
    assert trace["steps"][0]["result"]["evidence_valid"] is False


@pytest.mark.asyncio
async def test_unretrieved_citation_rejected(corpus):
    fake = final("answered", "F1 gate.", [{"source_id": "release-policy", "quote": "F1"}])
    config = yaml.safe_load(Path("configs/v1.yaml").read_text())
    config["max_iterations"] = 1
    trace = await Agent(corpus, ScriptedProvider([fake]), config).run("Promotion?")
    assert trace["answer"]["status"] == "abstain"
    assert trace["termination"] == "max_iterations"


@pytest.mark.asyncio
async def test_invalid_tool_and_step_limit(corpus):
    config = yaml.safe_load(Path("configs/v1.yaml").read_text())
    config["max_iterations"] = 2
    message = call("delete_all", {"reason": "Invalid operation"})
    trace = await Agent(corpus, ScriptedProvider([message, message]), config).run("Delete?")
    assert trace["iterations"] == 2 and trace["tool_errors"] == 2
    assert all(not s["valid"] for s in trace["steps"])


def test_datasets_and_harness():
    assert len(load_cases("datasets/dev_v1.jsonl")) == 35
    assert len(load_cases("datasets/golden_v1.jsonl")) == 18
    assert len({r.category for r in load_cases("datasets/dev_v1.jsonl")}) == 7
    case = EvalCase(
        id="x",
        category="failure-injection",
        question="x",
        expected_status="abstain",
        reference="Cannot verify",
        max_steps=2,
        failure="timeout",
    )
    trace = {
        "answer": {"status": "answered", "answer": "Wrong", "sources": []},
        "steps": [],
        "termination": "answered",
        "iterations": 1,
        "tool_errors": 2,
        "tokens": 1,
        "usage_complete": True,
        "latency_seconds": 0.1,
    }
    assert assess(case, trace)["failure_class"] == "cascading_soft_failure"


def test_promotion_requires_real_judge():
    verdict = gate(
        {
            "pct_ground_truth_passed": 1.0,
            "tool_call_correctness": 1.0,
            "hard_failure_rate": 0,
            "failure_injection_safe": 1,
            "usage_complete": 1,
        }
    )
    assert verdict["verdict"] == "REJECT"
    assert not verdict["checks"]["judge"]


def test_retrieval_bounds_and_sources(corpus):
    hits = corpus.search("API keys", source_id="security")
    assert hits and {r["source_id"] for r in hits} == {"security"}
    with pytest.raises(ValueError):
        corpus.search("keys", top_k=100)


@pytest.mark.asyncio
async def test_specific_feedback_preserves_clarification_without_retrieval(corpus):
    class CapturingProvider(ScriptedProvider):
        async def complete(self, messages, *args):
            if len(messages) > 2:
                repair = messages[-1]["content"]
                assert "Preserve your intended" in repair
                assert "clarify and abstain do not need citations" in repair
                assert "Do not retrieve policy about output validation" in repair
            return await super().complete(messages, *args)

    config = yaml.safe_load(Path("configs/v1.yaml").read_text())
    config["validation_feedback"] = "specific"
    provider = CapturingProvider(
        [
            {"content": 'clarify\n{"status":"clarify","answer":"Which options?","sources":[]}'},
            final("clarify", "Which options?"),
        ]
    )
    trace = await Agent(corpus, provider, config).run("Should I use that one?")
    assert trace["answer"]["status"] == "clarify"
    assert trace["iterations"] == 2
    assert all(step["event"] != "tool_call" for step in trace["steps"])


@pytest.mark.parametrize(
    "wrapper", ["clarify\n{}", "```json\n{}\n```", "<tool_call>\n{}\n</tool_call>"]
)
def test_final_wrapper_normalization_preserves_values(wrapper):
    payload = '{"status":"clarify","answer":"Which options?","sources":[]}'
    result, changed = parse_final(wrapper.format(payload), normalize=True)
    assert result.status == "clarify" and result.answer == "Which options?"
    assert changed
    with pytest.raises(ValueError):
        parse_final(wrapper.format(payload))


@pytest.mark.parametrize(
    "content",
    [
        'answered\n{"status":"clarify","answer":"Which options?","sources":[]}',
        'Untrusted prose {"status":"clarify","answer":"Which options?","sources":[]}',
        '{"status":"clarify","answer":"Which options?","sources":[]} {}',
    ],
)
def test_final_wrapper_normalization_rejects_ambiguous_or_mismatched_output(content):
    with pytest.raises(ValueError):
        parse_final(content, normalize=True)


def test_tool_wrapper_cannot_turn_function_arguments_into_an_answer():
    with pytest.raises(ValueError):
        parse_final(
            '<tool_call>\n{"name":"search","arguments":{"query":"x"}}\n</tool_call>', normalize=True
        )
