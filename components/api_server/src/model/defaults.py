"""Default attributes for model classes."""

from typing import Any

from shared_data_model import DATA_MODEL


def default_source_parameters(metric_type: str, source_type: str):
    """Return the source parameters with their default values for the specified metric."""
    parameters = DATA_MODEL.sources[source_type].parameters.items()
    return {key: value.default_value for key, value in parameters if metric_type in value.metrics}


def default_metric_attributes(metric_type: str):
    """Return the metric attributes with their default values for the specified metric type."""
    metric = DATA_MODEL.metrics[metric_type]
    return {
        "type": metric_type,
        "sources": {},
        "name": None,
        "scale": metric.default_scale,
        "unit": None,
        "addition": metric.addition,
        "accept_debt": False,
        "debt_target": None,
        "direction": None,
        "target": metric.target,
        "near_target": metric.near_target,
        "tags": metric.tags,
    }


def default_subject_attributes(subject_type: str) -> dict[str, Any]:
    """Return the default attributes for the subject."""
    subject = DATA_MODEL.subjects[subject_type]
    return {"type": subject_type, "name": None, "description": subject.description, "metrics": {}}
