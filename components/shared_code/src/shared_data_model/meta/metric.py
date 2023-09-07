"""Data model metrics."""

from typing import Self

from pydantic import ConfigDict, Field, model_validator

from .base import DescribedModel, StrEnum
from .unit import Unit


class Addition(StrEnum):
    """How measurements from sources should be combined."""

    MAX = "max"
    MIN = "min"
    SUM = "sum"


class Direction(StrEnum):
    """Specify whether more of the measured value is better or less of the measured value is better."""

    FEWER_IS_BETTER = "<"
    MORE_IS_BETTER = ">"


class Tag(StrEnum):
    """Metric tags."""

    ACCESSIBILITY = "accessibility"
    CI = "ci"
    MAINTAINABILITY = "maintainability"
    PERFORMANCE = "performance"
    PROCESS_EFFICIENCY = "process efficiency"
    SECURITY = "security"
    TEST_QUALITY = "test quality"
    TESTABILITY = "testability"


class Metric(DescribedModel):
    """Base model for metrics."""

    model_config = ConfigDict(validate_default=True)

    scales: list[str] = Field(["count"], min_length=1)
    default_scale: str = "count"
    unit: Unit = Unit.NONE
    addition: Addition = Addition.SUM
    direction: Direction = Direction.FEWER_IS_BETTER
    target: str = "0"
    near_target: str = "10"
    sources: list[str] = Field(..., min_length=1)
    tags: list[Tag] = []
    rationale: str = ""  # Answers the question "Why measure this metric?", included in documentation and UI
    rationale_urls: list[str] = []
    explanation: str | None = ""  # Optional explanation of concepts in text format, included in documentation and UI
    explanation_urls: list[str] = []
    documentation: str | None = ""  # Optional documentation in Markdown format, only included in the documentation

    @model_validator(mode="after")
    def set_default_scale(self) -> Self:
        """If the metric supports just one scale, make that scale the default scale."""
        self.default_scale = self.scales[0] if len(self.scales) == 1 else self.default_scale
        return self
