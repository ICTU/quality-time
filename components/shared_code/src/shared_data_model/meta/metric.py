"""Data model metrics."""

from enum import StrEnum, auto
from typing import Self

from pydantic import ConfigDict, Field, model_validator

from .base import DocumentedModel
from .unit import Unit


class Addition(StrEnum):
    """How measurements from sources should be combined."""

    MAX = auto()
    MIN = auto()
    SUM = auto()


class Direction(StrEnum):
    """Specify whether more of the measured value is better or less of the measured value is better."""

    FEWER_IS_BETTER = "<"
    MORE_IS_BETTER = ">"


class Tag(StrEnum):
    """Metric tags."""

    CI = auto()
    MAINTAINABILITY = auto()
    PERFORMANCE = auto()
    PROCESS_EFFICIENCY = "process efficiency"
    SECURITY = auto()
    TEST_QUALITY = "test quality"
    TESTABILITY = auto()


class Metric(DocumentedModel):
    """Base model for metrics."""

    model_config = ConfigDict(validate_default=True)

    scales: list[str] = Field(["count"], min_length=1)
    default_scale: str = "count"
    unit: Unit = Unit.NONE
    unit_singular: Unit = Unit.NONE
    addition: Addition = Addition.SUM
    direction: Direction = Direction.FEWER_IS_BETTER
    target: str = "0"
    near_target: str = "10"
    evaluate_targets: bool = True
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

    @model_validator(mode="after")
    def check_unit(self) -> Self:
        """Check that if the singular unit is not none, neither is the plural unit, and vice versa.

        Both units can be none when the metric has a version scale or when the measurement scale is otherwise
        dimensionless, such as with the sentiment metric.
        """
        if (self.unit, self.unit_singular).count(Unit.NONE) == 1:
            missing = "singular" if self.unit_singular == Unit.NONE else "plural"
            msg = f"The {missing} version of the unit of {self.name} is missing"
            raise ValueError(msg)
        return self
