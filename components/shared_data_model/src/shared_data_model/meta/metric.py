"""Data model metrics."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, validator  # pylint: disable=no-name-in-module

from .base import DescribedModel
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
    rationale: Optional[str] = ""
    rationale_urls: list[str] = []
    explanation: Optional[str] = ""
    explanation_urls: list[str] = []

    @validator("default_scale", always=True)
    def set_default_scale(cls, default_scale, values):  # pylint: disable=no-self-argument
        """If the metric supports just one scale, make that scale the default scale."""
        scales = values.get("scales", [])
        return scales[0] if len(scales) == 1 else default_scale


class Metrics(BaseModel):  # pylint: disable=too-few-public-methods
    """Metrics mapping."""

    __root__: dict[str, Metric]

    def __getitem__(self, key: str) -> Metric:
        """Return the metric with the specified key."""
        return self.__root__[key]
