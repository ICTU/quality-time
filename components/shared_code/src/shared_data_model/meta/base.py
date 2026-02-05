"""Data model base classes."""

import string
from typing import Self

from pydantic import BaseModel, Field, model_validator

from shared.utils.functions import slugify
from shared.utils.version import REFERENCE_DOCUMENTATION_URL


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


class DocumentedModel(DescribedModel):
    """Extend the described model with a reference documentation URL."""

    reference_documentation_url: str | None = None  # Set automatically by set_reference_documentation_url() below

    @model_validator(mode="after")
    def set_reference_documentation_url(self) -> Self:
        """Set the reference documentation URL based on the metric name."""
        self.reference_documentation_url = f"{REFERENCE_DOCUMENTATION_URL}{slugify(self.name)}"
        return self
