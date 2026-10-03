from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_id: str
    quote: str = Field(min_length=1)


class Answer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["answered", "abstain", "clarify"]
    answer: str = Field(min_length=1)
    sources: list[Citation] = Field(default_factory=list)

    @model_validator(mode="after")
    def cited(self):
        if self.status == "answered" and not self.sources:
            raise ValueError("Answered responses require evidence citations")
        return self


class Query(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=3, max_length=4000)


class EvalCase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    category: str
    question: str
    expected_status: Literal["answered", "abstain", "clarify"]
    reference: str
    required_terms: list[str] = Field(default_factory=list)
    required_sources: list[str] = Field(default_factory=list)
    max_steps: int = Field(ge=1, le=12)
    failure: Literal["timeout", "malformed", "unavailable"] | None = None
