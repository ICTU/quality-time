"""Measurement model classes."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar

from shared.model.metric import Metric

from collector_utilities.type import URL, ErrorMessage, JSONList, Value

from .entity import Entities
from .issue_status import IssueStatus


@dataclass
class SourceMeasurement:
    """Class to hold measurement values, entities, and error messages from collecting the measurement from a source."""

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

    def entities_to_store(self) -> JSONList:
        """Return the entities which should be stored, omitting ephemeral attributes."""
        return [
            # only include the attributes of type Value, so native objects like datetime can be used as ephemeral attrs
            {key: val for key, val in entity.items() if isinstance(val, Value)}
            for entity in self.get_entities()
        ]

    def as_dict(self, max_entities: int | None = None) -> dict[str, Value | JSONList | ErrorMessage | URL | None]:
        """Return the source measurement as dict."""
        return {
            "value": self.value,
            "total": self.total,
            "entities": self.entities_to_store()[:max_entities],
            "connection_error": self.connection_error,
            "parse_error": self.parse_error,
            "api_url": self.api_url,
            "landing_url": self.landing_url,
            "source_uuid": self.source_uuid,
        }


@dataclass
class MetricMeasurement:
    """Class to hold measurements from one or more sources for one metric."""

    DEFAULT_MAX_ENTITIES: ClassVar[int] = 250

    metric: Metric
    sources: Sequence[SourceMeasurement]
    issue_statuses: Sequence[IssueStatus]
    metric_uuid: str | None = None
    report_uuid: str | None = None

    @property
    def has_error(self) -> bool:
        """Return whether this measurement has one or more errors."""
        return any(source_measurement.has_error for source_measurement in self.sources)

    @property
    def max_entities(self) -> int | None:
        """Return the maximum number of entities (violations, issues, etc.) to store per source per measurement."""
        # We don't limit the number of security warnings so we can detect duplicate CVEs between different sources
        return None if self.metric.type() == "security_warnings" else self.DEFAULT_MAX_ENTITIES

    def as_dict(self) -> dict:
        """Return the metric measurement as dict."""
        measurement = {
            "sources": [source_measurement.as_dict(self.max_entities) for source_measurement in self.sources],
            "has_error": self.has_error,
            "metric_uuid": self.metric_uuid,
            "report_uuid": self.report_uuid,
            "source_parameter_hash": self.metric.source_parameter_hash(),
        }
        if self.issue_statuses:
            measurement["issue_status"] = [issue_status.as_dict() for issue_status in self.issue_statuses]
        return measurement
