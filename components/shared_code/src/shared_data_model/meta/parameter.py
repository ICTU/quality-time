"""Data model source parameters."""

from typing import Self

from pydantic import ConfigDict, Field, HttpUrl, model_validator

from .base import NamedModel, StrEnum


class ParameterType(StrEnum):
    """Parameter type."""

    DATE = "date"
    INTEGER = "integer"
    MULTIPLE_CHOICE = "multiple_choice"
    MULTIPLE_CHOICE_WITH_ADDITION = "multiple_choice_with_addition"
    PASSWORD = "password"  # nosec # noqa: S105
    SINGLE_CHOICE = "single_choice"
    STRING = "string"
    URL = "url"


class Parameter(NamedModel):
    """Source parameter model."""

    model_config = ConfigDict(validate_default=True)

    short_name: str = ""
    help: str | None = None  # noqa: A003
    help_url: HttpUrl | None = None
    type: ParameterType  # noqa: A003
    placeholder: str | None = None
    mandatory: bool = False
    default_value: str | list[str] = ""
    unit: str | None = None
    metrics: list[str] = Field(..., min_length=1)
    values: list[str] | None = None
    api_values: dict[str, str] | None = None
    validate_on: list[str] | None = None

    @model_validator(mode="after")
    def set_short_name(self) -> Self:
        """Set the short name if no value was supplied."""
        if not self.short_name:
            self.short_name = self.name.lower()
        return self

    @model_validator(mode="after")
    def check_help(self) -> Self:
        """Check that not both help and help URL are set."""
        if self.help_url and self.help:
            msg = f"Parameter {self.name} has both help and help_url"
            raise ValueError(msg)
        if self.help:
            self.check_punctuation("help", self.help)
        return self

    @model_validator(mode="after")
    def check_placeholder(self) -> Self:
        """Check that a placeholder exist if the parameter type is multiple choice."""
        if self.is_multiple_choice() and not self.placeholder:
            msg = f"Parameter {self.name} is multiple choice but has no placeholder"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def check_default_value(self) -> Self:
        """Check that the default value is a list if the parameter type is multiple choice."""
        if self.is_multiple_choice() and not isinstance(self.default_value, list):
            msg = f"Parameter {self.name} is multiple choice but default_value is not a list"
            raise ValueError(msg)
        if self.is_multiple_choice_with_addition() and isinstance(self.default_value, list) and self.default_value:
            msg = f"Parameter {self.name} is multiple choice with addition but default_value is not empty"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def check_values(self) -> Self:
        """Check that the number of values of the parameter matches the parameter type."""
        if self.type == ParameterType.MULTIPLE_CHOICE and (self.values is None or len(self.values) <= 1):
            msg = f"Parameter {self.name} is multiple choice but has fewer than two values"
            raise ValueError(msg)
        if self.is_multiple_choice_with_addition() and self.values:
            msg = f"Parameter {self.name} is multiple choice with addition but has values"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def check_api_values(self) -> Self:
        """Check that if the parameter has API values, the API values match with the values."""
        if self.api_values and not self.values:
            msg = f"Parameter {self.name} has api_values but no values"
            raise ValueError(msg)
        if self.api_values and self.values and not set(self.api_values.keys()).issubset(set(self.values)):
            msg = f"Parameter {self.name} has api_values keys that are not listed in values"
            raise ValueError(msg)
        return self

    def is_multiple_choice(self) -> bool:
        """Return whether the parameter is multiple choice."""
        return self.type in (ParameterType.MULTIPLE_CHOICE, ParameterType.MULTIPLE_CHOICE_WITH_ADDITION)

    def is_multiple_choice_with_addition(self) -> bool:
        """Return whether the parameter is multiple choice with addition."""
        return bool(self.type == ParameterType.MULTIPLE_CHOICE_WITH_ADDITION)
