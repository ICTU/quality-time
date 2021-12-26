"""Model queries."""


def is_password_parameter(data_model, source_type: str, parameter: str) -> bool:
    """Return whether the parameter of the source type is a password."""
    # If the parameter key can't be found (this can happen when the parameter is removed from the data model),
    # err on the safe side and assume it was a password type
    parameter_type = (
        data_model["sources"].get(source_type, {}).get("parameters", {}).get(parameter, dict(type="password"))["type"]
    )
    return str(parameter_type) == "password"
