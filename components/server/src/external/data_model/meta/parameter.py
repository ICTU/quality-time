"""Data model source parameters."""

from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, Field, HttpUrl, validator  # pylint: disable=no-name-in-module

from .base import NamedModel


class ParameterType(str, Enum):
    """Parameter type."""

    DATE = "date"
    INTEGER = "integer"
    MULTIPLE_CHOICE = "multiple_choice"
    MULTIPLE_CHOICE_WITH_ADDITION = "multiple_choice_with_addition"
    PASSWORD = "password"  # nosec
    SINGLE_CHOICE = "single_choice"
    STRING = "string"
    URL = "url"


class Parameter(NamedModel):  # pylint: disable=too-few-public-methods
    """Source parameter model."""

    short_name: Optional[str] = None
    help: Optional[str] = Field(None, regex=r".+\.")
    help_url: Optional[HttpUrl] = None
    type: ParameterType
    placeholder: Optional[str] = None
    mandatory: bool = False
    default_value: Union[str, list[str]] = ""
    unit: Optional[str] = None
    metrics: list[str] = Field(..., min_items=1)
    values: Optional[list[str]] = None
    api_values: Optional[dict[str, str]] = None
    validate_on: Optional[list[str]] = None

    # pylint: disable=no-self-argument,no-self-use

    @validator("short_name", always=True)
    def set_short_name(cls, short_name: Optional[str], values) -> Optional[str]:
        """Set the short name if no value was supplied."""
        return values["name"].lower() if not short_name else short_name

    @validator("help_url", always=True)
    def check_help(cls, help_url: Optional[HttpUrl], values) -> Optional[HttpUrl]:
        """Check that not both help and help URL are set."""
        if help_url and values.get("help"):
            raise ValueError(f"Parameter {values['name']} has both help and help_url")
        return help_url

    @validator("placeholder", always=True)
    def check_placeholder(cls, placeholder: Optional[str], values) -> Optional[str]:
        """Check that a placeholder exist if the parameter type is multiple choice."""
        if cls.is_multiple_choice(values) and not placeholder:
            raise ValueError(f"Parameter {values['name']} is multiple choice but has no placeholder")
        return placeholder

    @validator("default_value", always=True)
    def check_default_value(cls, default_value: Union[str, list[str]], values) -> Union[str, list[str]]:
        """Check that the default value is a list if the parameter type is multiple choice."""
        if cls.is_multiple_choice(values) and not isinstance(default_value, list):
            raise ValueError(f"Parameter {values['name']} is multiple choice but default_value is not a list")
        if cls.is_multiple_choice_with_addition(values) and isinstance(default_value, list) and default_value:
            raise ValueError(
                f"Parameter {values['name']} is multiple choice with addition but default_value is not empty"
            )
        return default_value

    @validator("values", always=True)
    def check_values(cls, values_list: Optional[list[str]], values) -> Optional[list[str]]:
        """Check that the there are at least two values if the parameter is multiple choice without addition."""
        parameter_type = values.get("type")
        if parameter_type == ParameterType.MULTIPLE_CHOICE and (values_list is None or len(values_list) < 2):
            raise ValueError(f"Parameter {values['name']} is multiple choice but has fewer than two values")
        if cls.is_multiple_choice_with_addition(values) and values_list:
            raise ValueError(f"Parameter {values['name']} is multiple choice with addition but has values")
        return values_list

    @validator("api_values")
    def check_api_values(cls, api_values: Optional[dict[str, str]], values) -> Optional[dict[str, str]]:
        """Check that if the parameter has API values it also has values."""
        if api_values and not values.get("values"):
            raise ValueError(f"Parameter {values['name']} has api_values but no values")
        if api_values and not set(api_values.keys()).issubset(set(values.get("values", []))):
            raise ValueError(f"Parameter {values['name']} has api_values keys that are not listed in values")
        return api_values

    @classmethod
    def is_multiple_choice(cls, values) -> bool:
        """Return whether the parameter is multiple choice."""
        return values.get("type") in (ParameterType.MULTIPLE_CHOICE, ParameterType.MULTIPLE_CHOICE_WITH_ADDITION)

    @classmethod
    def is_multiple_choice_with_addition(cls, values) -> bool:
        """Return whether the parameter is multiple choice with addition."""
        return bool(values.get("type") == ParameterType.MULTIPLE_CHOICE_WITH_ADDITION)


class Parameters(BaseModel):  # pylint: disable=too-few-public-methods
    """Parameter mapping."""

    __root__: dict[str, Parameter]
