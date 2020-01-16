"""Model transformations."""

from typing import List, Union

from server_utilities.type import MetricId, SourceId, SubjectId
from .iterators import sources


def hide_credentials(data_model, *reports) -> None:
    """Hide the credentials in the reports."""
    data_model_sources = data_model["sources"]
    for report in reports:
        for _, source in sources(report):
            for parameter_key, parameter_value in source.get("parameters", {}).items():
                if parameter_value and \
                        data_model_sources[source["type"]]["parameters"][parameter_key]["type"] == "password":
                    source["parameters"][parameter_key] = "this string replaces credentials"


def mass_change_source_parameter(report, source_type: str, parameter_key: str, old_value, new_value) -> \
        List[Union[SubjectId, MetricId, SourceId]]:
    """Change the parameter with the specified key of all sources of the specified type and with the same old value to
    the new value. Return the ids of the changed subjects, metrics, and sources."""
    changed_ids: List[Union[SubjectId, MetricId, SourceId]] = []
    for subject_uuid, subject in report["subjects"].items():
        for metric_uuid, metric in subject["metrics"].items():
            for source_uuid, source in metric["sources"].items():
                if source["type"] == source_type and source["parameters"][parameter_key] == old_value:
                    source["parameters"][parameter_key] = new_value
                    if subject_uuid not in changed_ids:
                        changed_ids.append(subject_uuid)
                    if metric_uuid not in changed_ids:
                        changed_ids.append(metric_uuid)
                    changed_ids.append(source_uuid)
    return changed_ids
