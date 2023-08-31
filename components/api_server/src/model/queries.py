"""Model queries."""

from shared_data_model import DATA_MODEL


def is_password_parameter(source_type: str, parameter: str, data_model: dict | None = None) -> bool:
    """Return whether the parameter of the source type is a password."""
    # If the parameter key can't be found (this can happen when the parameter is removed from the data model),
    # err on the safe side and assume it was a password type
    if data_model is None:
        data_model = DATA_MODEL.dict()
    try:
        return bool(data_model["sources"][source_type]["parameters"][parameter]["type"] == "password")
    except KeyError:
        return True
