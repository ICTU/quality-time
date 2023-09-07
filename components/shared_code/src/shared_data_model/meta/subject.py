"""Data model subject."""

from pydantic import Field

from .base import DescribedModel


class Subject(DescribedModel):
    """Base model for subjects."""

    metrics: list[str] = Field(..., min_length=1)
