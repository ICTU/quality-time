"""Model iterators."""

from typing import TYPE_CHECKING

from shared.model.iterators import issue_trackers, sources
from shared_data_model.parameters import PASSWORD_PARAMETERS

from .queries import is_password_parameter

if TYPE_CHECKING:
    from collections.abc import Iterator

    from shared.model.source import Source


def credential_holders(*reports, data_model: dict | None = None) -> Iterator[tuple[dict, list[str]]]:
    """Yield (parameters, keys) for each item in the reports holding credentials. Keys with empty values are skipped."""
    for source in sources(*reports):
        yield source["parameters"], _password_parameter_keys(source, data_model)
    for issue_tracker in issue_trackers(*reports):
        parameters = issue_tracker.get("parameters") or {}
        if parameters:
            yield parameters, [key for key in PASSWORD_PARAMETERS if parameters.get(key)]


def _password_parameter_keys(source: Source, data_model: dict | None = None) -> list[str]:
    """Return the password parameter keys of the source with a truthy value."""
    parameters = source.get("parameters", {}).items()
    return [key for key, value in parameters if value and is_password_parameter(source["type"], key, data_model)]
