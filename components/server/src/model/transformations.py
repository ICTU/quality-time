"""Model transformations."""

from typing import Iterator, List

from server_utilities.functions import unique
from server_utilities.type import EditScope, ItemId
from .iterators import sources as iter_sources


def hide_credentials(data_model, *reports) -> None:
    """Hide the credentials in the reports."""
    data_model_sources = data_model["sources"]
    for report in reports:
        for _, source in iter_sources(report):
            for parameter_key, parameter_value in source.get("parameters", {}).items():
                if parameter_value and \
                        data_model_sources[source["type"]]["parameters"][parameter_key]["type"] == "password":
                    source["parameters"][parameter_key] = "this string replaces credentials"


def change_source_parameter(data, parameter_key: str, old_value, new_value, scope: EditScope) -> List[ItemId]:
    """Change the parameter with the specified key of all sources of the specified type and with the same old value to
    the new value. Return the ids of the changed reports, subjects, metrics, and sources."""

    def sources_to_change() -> Iterator:
        """Return the sources to change."""
        reports = data.reports if scope == "reports" else [data.report]
        for report in reports:
            subjects = {data.subject_uuid: data.subject} if scope in ["subject", "metric", "source"] \
                else report["subjects"]
            for subject_uuid, subject in subjects.items():
                metrics = {data.metric_uuid: data.metric} if scope in ["metric", "source"] else subject["metrics"]
                for metric_uuid, metric in metrics.items():
                    sources = {data.source_uuid: data.source} if scope == "source" else metric["sources"]
                    for source_uuid, source_to_change in sources.items():
                        yield source_to_change, [report["report_uuid"], subject_uuid, metric_uuid, source_uuid]

    changed_ids: List[ItemId] = []
    for source, uuids in sources_to_change():
        if source["type"] == data.source["type"] and source["parameters"].get(parameter_key, "") == old_value:
            source["parameters"][parameter_key] = new_value
            changed_ids.extend(uuids)
    return list(unique(changed_ids))
