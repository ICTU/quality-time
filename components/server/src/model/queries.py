"""Model queries."""

from typing import Optional


def is_password_parameter(data_model, source_type: str, parameter: str) -> bool:
    """Return whether the parameter of the source type is a password."""
    # If the parameter key can't be found (this can happen when the parameter is removed from the data model),
    # err on the safe side and assume it was a password type
    parameter_type = (
        data_model["sources"].get(source_type, {}).get("parameters", {}).get(parameter, dict(type="password"))["type"]
    )
    return str(parameter_type) == "password"


def get_attribute_type(entity: dict[str, list[dict[str, str]]], attribute_key: Optional[str]) -> str:
    """Look up the type of an entity attribute."""
    attribute_type = (
        [attribute for attribute in entity["attributes"] if attribute["key"] == attribute_key][0].get("type", "text")
        if entity and attribute_key
        else "text"
    )
    return str(attribute_type)
