"""Data model source parameters."""

from enum import Enum

from pydantic import Field, HttpUrl, validator

from .base import MappedModel, NamedModel


class ParameterType(str, Enum):
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

    short_name: str | None = None
    help: str | None = Field(None, regex=r".+\.")  # noqa: A003
    help_url: HttpUrl | None = None
    type: ParameterType  # noqa: A003
    placeholder: str | None = None
    mandatory: bool = False
    default_value: str | list[str] = ""
    unit: str | None = None
    metrics: list[str] = Field(..., min_items=1)
    values: list[str] | None = None
    api_values: dict[str, str] | None = None
    validate_on: list[str] | None = None

    @validator("short_name", always=True)
    def set_short_name(cls, short_name: str | None, values) -> str | None:
        """Set the short name if no value was supplied."""
        return short_name if short_name else values["name"].lower()

    @validator("help_url", always=True)
    def check_help(cls, help_url: HttpUrl | None, values) -> HttpUrl | None:
        """Check that not both help and help URL are set."""
        if help_url and values.get("help"):
            msg = f"Parameter {values['name']} has both help and help_url"
            raise ValueError(msg)
        return help_url

    @validator("placeholder", always=True)
    def check_placeholder(cls, placeholder: str | None, values) -> str | None:
        """Check that a placeholder exist if the parameter type is multiple choice."""
        if cls.is_multiple_choice(values) and not placeholder:
            msg = f"Parameter {values['name']} is multiple choice but has no placeholder"
            raise ValueError(msg)
        return placeholder

    @validator("default_value", always=True)
    def check_default_value(cls, default_value: str | list[str], values) -> str | list[str]:
        """Check that the default value is a list if the parameter type is multiple choice."""
        if cls.is_multiple_choice(values) and not isinstance(default_value, list):
            msg = f"Parameter {values['name']} is multiple choice but default_value is not a list"
            raise ValueError(msg)
        if cls.is_multiple_choice_with_addition(values) and isinstance(default_value, list) and default_value:
            msg = f"Parameter {values['name']} is multiple choice with addition but default_value is not empty"
            raise ValueError(
                msg,
            )
        return default_value

    @validator("values", always=True)
    def check_values(cls, values_list: list[str] | None, values) -> list[str] | None:
        """Check that the there are at least two values if the parameter is multiple choice without addition."""
        parameter_type = values.get("type")
        if parameter_type == ParameterType.MULTIPLE_CHOICE and (values_list is None or len(values_list) <= 1):
            msg = f"Parameter {values['name']} is multiple choice but has fewer than two values"
            raise ValueError(msg)
        if cls.is_multiple_choice_with_addition(values) and values_list:
            msg = f"Parameter {values['name']} is multiple choice with addition but has values"
            raise ValueError(msg)
        return values_list

    @validator("api_values")
    def check_api_values(cls, api_values: dict[str, str] | None, values) -> dict[str, str] | None:
        """Check that if the parameter has API values it also has values."""
        if api_values and not values.get("values"):
            msg = f"Parameter {values['name']} has api_values but no values"
            raise ValueError(msg)
        if api_values and not set(api_values.keys()).issubset(set(values.get("values", []))):
            msg = f"Parameter {values['name']} has api_values keys that are not listed in values"
            raise ValueError(msg)
        return api_values

    @classmethod
    def is_multiple_choice(cls, values) -> bool:
        """Return whether the parameter is multiple choice."""
        return values.get("type") in (ParameterType.MULTIPLE_CHOICE, ParameterType.MULTIPLE_CHOICE_WITH_ADDITION)

    @classmethod
    def is_multiple_choice_with_addition(cls, values) -> bool:
        """Return whether the parameter is multiple choice with addition."""
        return bool(values.get("type") == ParameterType.MULTIPLE_CHOICE_WITH_ADDITION)


class Parameters(MappedModel[Parameter]):
    """Parameter mapping."""
