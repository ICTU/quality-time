"""Data model source model."""

from typing import Self

from pydantic import Field, HttpUrl, SerializeAsAny, model_validator

from .base import DescribedModel, NamedModel
from .entity import Entity
from .parameter import Parameter


class Configuration(NamedModel):
    """Configuration for specific metrics."""

    metrics: list[str] = Field(..., min_length=1)
    value: list[str] = Field(..., min_length=1)


class Source(DescribedModel):
    """The source model extends the base model with source parameters and measurement entities."""

    url: HttpUrl | None = None
    documentation: dict[str, str] | None = None  # Documentation in Markdown format
    configuration: dict[str, Configuration] = {}
    parameters: dict[str, SerializeAsAny[Parameter]]
    entities: dict[str, Entity] = {}
    issue_tracker: bool | None = False

    @model_validator(mode="after")
    def check_parameters(self) -> Self:
        """Check that if the source has a landing URL parameter it also has a URL parameter."""
        if "landing_url" in self.parameters and "url" not in self.parameters:
            msg = f"Source {self.name} has a landing URL but no URL"
            raise ValueError(msg)
        for parameter_key, parameter in self.parameters.items():
            for parameter_to_validate_on in parameter.validate_on or []:
                if parameter_to_validate_on not in self.parameters:
                    msg = (
                        f"Source {self.name} should validate parameter {parameter_key} when parameter "
                        f"{parameter_to_validate_on} changes, but source {self.name} has no parameter "
                        f"{parameter_to_validate_on}"
                    )
                    raise ValueError(msg)
        return self
