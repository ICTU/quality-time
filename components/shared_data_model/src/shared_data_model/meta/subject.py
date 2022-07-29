"""Data model subject."""

from pydantic import Field

from .base import DescribedModel, MappedModel


class Subject(DescribedModel):  # pylint: disable=too-few-public-methods
    """Base model for subjects."""

    metrics: list[str] = Field(..., min_items=1)


class Subjects(MappedModel[Subject]):  # pylint: disable=too-few-public-methods
    """Subjects mapping."""
