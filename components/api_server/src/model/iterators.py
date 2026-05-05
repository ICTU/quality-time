"""Model iterators."""

from typing import TYPE_CHECKING

from .queries import is_password_parameter

if TYPE_CHECKING:
    from collections.abc import Iterator

    from shared.model.source import Source


def subjects(*reports) -> Iterator:
    """Return all subjects in the reports."""
    for report in reports:
        yield from report.get("subjects", {}).values()


def metrics(*reports) -> Iterator:
    """Return all metrics in the reports."""
    for subject in subjects(*reports):
        yield from subject.get("metrics", {}).values()


def sources(*reports) -> Iterator:
    """Return all sources in the reports."""
    for metric in metrics(*reports):
        yield from metric.get("sources", {}).values()


def issue_trackers(*reports) -> Iterator:
    """Return all issue trackers in the reports."""
    for report in reports:
        if issue_tracker := report.get("issue_tracker"):
            yield issue_tracker


def credential_holders(*reports, data_model: dict | None = None) -> Iterator[tuple[dict, list[str]]]:
    """Yield (parameters, keys) for each item in the reports holding credentials. Keys with empty values are skipped."""
    for source in sources(*reports):
        yield source["parameters"], _password_parameter_keys(source, data_model)
    for issue_tracker in issue_trackers(*reports):
        parameters = issue_tracker.get("parameters") or {}
        if parameters:
            yield parameters, [key for key in ("password", "private_token") if parameters.get(key)]


def _password_parameter_keys(source: Source, data_model: dict | None = None) -> list[str]:
    """Return the password parameter keys of the source with a truthy value."""
    parameters = source.get("parameters", {}).items()
    return [key for key, value in parameters if value and is_password_parameter(source["type"], key, data_model)]
