"""Data model base classes."""

import string
from enum import Enum
from typing import Self, cast

from pydantic import BaseModel, Field, model_validator


class StrEnum(str, Enum):
    """Enums that use strings as values."""

    __slots__ = ()

    def __format__(self, _spec) -> str:
        """Override to return the value."""
        return cast(str, self.value)


class NamedModel(BaseModel):
    """Extend the Pydantic base model with a name."""

    name: str = Field(..., pattern=r"[^\.]+")  # Disallow dots so names can be used as key

    def check_punctuation(self, field_name: str, field_value: str) -> None:
        """Check that the value of the field ends with punctuation."""
        if not field_value.endswith(tuple(string.punctuation)):
            msg = f"The {field_name} of {self.name} does not end with punctuation"
            raise ValueError(msg)


class DescribedModel(NamedModel):
    """Extend the named model with a description."""

    description: str = Field(..., pattern=r".+")

    @model_validator(mode="after")
    def check_description(self) -> Self:
        """Check the description."""
        self.check_punctuation("description", self.description)
        return self
