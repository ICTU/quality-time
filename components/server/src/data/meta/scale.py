"""Data model scales."""

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from .base import DescribedModel


class Scale(DescribedModel):  # pylint: disable=too-few-public-methods
    """Base model for scales."""


class Scales(BaseModel):  # pylint: disable=too-few-public-methods
    """Scales mapping."""

    __root__: dict[str, Scale]
