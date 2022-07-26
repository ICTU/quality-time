"""Data model base classes."""

import string
from collections.abc import MappingView
from typing import Generic, TypeVar

from pydantic import BaseModel, Field, validator  # pylint: disable=no-name-in-module
from pydantic.generics import GenericModel


class NamedModel(BaseModel):  # pylint: disable=too-few-public-methods
    """Extend the Pydantic base model with a name."""

    name: str = Field(..., regex=r"[^\.]+")  # Disallow dots so names can be used as key


class DescribedModel(NamedModel):  # pylint: disable=too-few-public-methods
    """Extend the named model with a description."""

    description: str = Field(..., regex=r".+")

    @validator("description")
    def set_description(cls, description):  # pylint: disable=no-self-argument
        """Add a dot if needed."""
        return description if description.endswith(tuple(string.punctuation)) else description + "."


ValueT = TypeVar("ValueT")


class MappedModel(GenericModel, Generic[ValueT]):  # pylint: disable=too-few-public-methods
    """Extend the Pydantic base model with a mapping."""

    __root__: dict[str, ValueT]

    def __getitem__(self, key: str) -> ValueT:
        """Return the model with the specified key."""
        return self.__root__[key]

    def items(self) -> MappingView[str, ValueT]:
        """Return all keys and values."""
        return self.__root__.items()
