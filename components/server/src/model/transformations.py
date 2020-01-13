"""Model transformations."""

from typing import Iterator


def _sources(report) -> Iterator:
    """Return all sources in the report."""
    for subject in report.get("subjects", {}).values():
        for metric in subject.get("metrics", {}).values():
            yield from metric.get("sources", {}).values()


def hide_credentials(data_model, *reports) -> None:
    """Hide the credentials in the reports."""
    data_model_sources = data_model["sources"]
    for report in reports:
        for source in _sources(report):
            for parameter_key, parameter_value in source.get("parameters", {}).items():
                if parameter_value and \
                        data_model_sources[source["type"]]["parameters"][parameter_key]["type"] == "password":
                    source["parameters"][parameter_key] = "this string replaces credentials"
