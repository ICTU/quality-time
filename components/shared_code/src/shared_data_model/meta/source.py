"""Data model source model."""

from typing import TYPE_CHECKING, Self

from pydantic import Field, HttpUrl, SerializeAsAny, model_validator

from .base import DescribedModel, NamedModel
from .parameter import DEFAULT_PARAMETER_LAYOUT, Parameter, ParameterGroup

if TYPE_CHECKING:
    from .entity import Entity


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
    parameter_layout: dict[str, ParameterGroup] = DEFAULT_PARAMETER_LAYOUT
    entities: dict[str, Entity] = {}
    issue_tracker: bool | None = False
    supported_versions_description: str | None = None  # The source versions that Quality-time supports, e.g. "≥10.2"
    deprecated: bool | None = False
    deprecation_url: HttpUrl | None = None  # URL to a GitHub issue

    @model_validator(mode="after")
    def check_parameters(self) -> Self:
        """Check the consistency of the source parameters."""
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

    @model_validator(mode="after")
    def check_deprecation_url(self) -> Self:
        """Check that deprecated sources have a deprecation URL."""
        if self.deprecated and self.deprecation_url is None:
            msg = f"Source {self.name} is deprecated but has no deprecation URL"
            raise ValueError(msg)
        return self
