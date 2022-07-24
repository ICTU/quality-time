"""Data model scales."""

from .base import DescribedModel, MappedModel


class Scale(DescribedModel):  # pylint: disable=too-few-public-methods
    """Base model for scales."""


class Scales(MappedModel[Scale]):  # pylint: disable=too-few-public-methods
    """Scales mapping."""
