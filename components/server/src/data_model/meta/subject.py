"""Data model subject."""

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

from .base import DescribedModel


class Subject(DescribedModel):  # pylint: disable=too-few-public-methods
    """Base model for subjects."""

    metrics: list[str] = Field(..., min_items=1)


class Subjects(BaseModel):  # pylint: disable=too-few-public-methods
    """Subjects mapping."""

    __root__: dict[str, Subject]
