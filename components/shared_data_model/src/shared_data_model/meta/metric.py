"""Data model metrics."""

from enum import Enum
from typing import Optional

from pydantic import Field, validator

from .base import DescribedModel, MappedModel
from .unit import Unit


class Addition(str, Enum):
    """How measurements from sources should be combined."""

    MAX = "max"
    MIN = "min"
    SUM = "sum"


class Direction(str, Enum):
    """Is more of the measured value better or is less of the measured value better?"""

    FEWER_IS_BETTER = "<"
    MORE_IS_BETTER = ">"


class Tag(str, Enum):
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

    scales: list[str] = Field(["count"], min_items=1)
    default_scale: str = "count"
    unit: Unit = Unit.NONE
    addition: Addition = Addition.SUM
    direction: Direction = Direction.FEWER_IS_BETTER
    target: str = "0"
    near_target: str = "10"
    sources: list[str] = Field(..., min_items=1)
    tags: list[Tag] = []
    rationale: str = ""  # Answers the question "Why measure this metric?", included in documentation and UI
    rationale_urls: list[str] = []
    explanation: Optional[str] = ""  # Optional explanation of concepts in text format, included in documentation and UI
    explanation_urls: list[str] = []
    documentation: Optional[str] = ""  # Optional documentation in Markdown format, only included in the documentation

    @validator("default_scale", always=True)
    def set_default_scale(cls, default_scale, values):  # pylint: disable=no-self-argument
        """If the metric supports just one scale, make that scale the default scale."""
        scales = values.get("scales", [])
        return scales[0] if len(scales) == 1 else default_scale


class Metrics(MappedModel[Metric]):  # pylint: disable=too-few-public-methods
    """Metrics mapping."""
