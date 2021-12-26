"""Data model base classes."""

import string

from pydantic import BaseModel, Field, validator  # pylint: disable=no-name-in-module


class NamedModel(BaseModel):  # pylint: disable=too-few-public-methods
    """Extend the Pydantic base model with a name."""

    name: str = Field(..., regex=r"[^\.]+")  # Disallow dots so names can be used as key


class DescribedModel(NamedModel):  # pylint: disable=too-few-public-methods
    """Extend the named model with a description."""

    description: str = Field(..., regex=r".+")

    @validator("description")
    def set_description(cls, description):  # pylint: disable=no-self-argument,no-self-use
        """Add a dot if needed."""
        return description if description.endswith(tuple(string.punctuation)) else description + "."
