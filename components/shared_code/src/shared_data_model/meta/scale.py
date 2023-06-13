"""Data model scales."""

from .base import DescribedModel, MappedModel


class Scale(DescribedModel):
    """Base model for scales."""


class Scales(MappedModel[Scale]):
    """Scales mapping."""
