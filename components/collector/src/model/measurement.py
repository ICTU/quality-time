"""Measurement model classes."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar

from shared.model.metric import Metric

from collector_utilities.type import URL, ErrorMessage, Value

from .entity import Entities
from .issue_status import IssueStatus


@dataclass
class SourceMeasurement:
    """Class to hold measurement values, entities, and error messages from collecting the measurement from a source."""

    MAX_ENTITIES: ClassVar[int] = 100  # The maximum number of entities (e.g. violations, issues) to send to the server

    value: Value | None = None
    total: Value | None = "100"
    entities: Entities | None = None
    connection_error: ErrorMessage | None = None
    parse_error: ErrorMessage | None = None
    api_url: URL | None = None
    landing_url: URL | None = None
    source_uuid: str | None = None

    def __post_init__(self):
        """Initialize fields that depend on other fields."""
        if self.has_error:
            self.total = None
        if self.value is None and self.entities is not None:
            self.value = str(len(self.entities))

    @property
    def has_error(self) -> bool:
        """Return whether the measurement had a connection or parse error."""
        return bool(self.connection_error or self.parse_error)

    def get_entities(self) -> Entities:
        """Return the measurement entities or an empty list if there are none."""
        return self.entities or Entities()

    def as_dict(self) -> dict[str, Value | Entities | ErrorMessage | URL | None]:
        """Return the source measurement as dict."""
        return {
            "value": self.value,
            "total": self.total,
            "entities": self.get_entities()[: self.MAX_ENTITIES],
            "connection_error": self.connection_error,
            "parse_error": self.parse_error,
            "api_url": self.api_url,
            "landing_url": self.landing_url,
            "source_uuid": self.source_uuid,
        }


@dataclass
class MetricMeasurement:
    """Class to hold measurements from one or more sources for one metric."""

    metric: Metric
    sources: Sequence[SourceMeasurement]
    issue_statuses: Sequence[IssueStatus]
    metric_uuid: str | None = None
    report_uuid: str | None = None

    @property
    def has_error(self) -> bool:
        """Return whether this measurement has one or more errors."""
        return any(source_measurement.has_error for source_measurement in self.sources)

    def as_dict(self) -> dict:
        """Return the metric measurement as dict."""
        measurement = {
            "sources": [source_measurement.as_dict() for source_measurement in self.sources],
            "has_error": self.has_error,
            "metric_uuid": self.metric_uuid,
            "report_uuid": self.report_uuid,
            "source_parameter_hash": self.metric.source_parameter_hash(),
        }
        if self.issue_statuses:
            measurement["issue_status"] = [issue_status.as_dict() for issue_status in self.issue_statuses]
        return measurement
