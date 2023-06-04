"""Data model base classes."""

import string
from collections.abc import ItemsView, ValuesView
from typing import Generic, TypeVar

from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel


class NamedModel(BaseModel):
    """Extend the Pydantic base model with a name."""

    name: str = Field(..., regex=r"[^\.]+")  # Disallow dots so names can be used as key


class DescribedModel(NamedModel):
    """Extend the named model with a description."""

    description: str = Field(..., regex=r".+")

    @validator("description")
    def set_description(cls, description: str) -> str:
        """Add a dot if needed."""
        return description if description.endswith(tuple(string.punctuation)) else description + "."


ValueT = TypeVar("ValueT")


class MappedModel(GenericModel, Generic[ValueT]):
    """Extend the Pydantic base model with a mapping."""

    __root__: dict[str, ValueT]

    def __getitem__(self, key: str) -> ValueT:
        """Return the model with the specified key."""
        return self.__root__[key]  # pragma: no feature-test-cover

    def get(self, key: str) -> ValueT | None:
        """Return the model with the specified key or None if the key does not exist."""
        return self.__root__.get(key)  # pragma: no feature-test-cover

    def items(self) -> ItemsView:
        """Return all keys and values."""
        return self.__root__.items()  # pragma: no feature-test-cover

    def values(self) -> ValuesView:
        """Return all values."""
        return self.__root__.values()  # pragma: no feature-test-cover
