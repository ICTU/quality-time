"""Measurement model classes."""

from collections.abc import Sequence

from collector_utilities.type import URL, ErrorMessage, Value

from .entity import Entities
from .issue_status import IssueStatus


class SourceMeasurement:
    """Class to hold measurement values, entities, and error messages from collecting the measurement from a source."""

    MAX_ENTITIES = 100  # The maximum number of entities (e.g. violations, warnings) to send to the server

    def __init__(  # noqa: PLR0913
        self,
        *,
        value: Value | None = None,
        total: Value = "100",
        entities: Entities | None = None,
        connection_error: ErrorMessage | None = None,
        parse_error: ErrorMessage | None = None,
    ) -> None:
        self.value = str(len(entities)) if value is None and entities is not None else value
        self.entities = Entities() if entities is None else entities
        self.parse_error = parse_error
        self.connection_error = connection_error
        self.total = None if self.has_error() else total
        self.api_url: URL | None = None
        self.landing_url: URL | None = None
        self.source_uuid: str | None = None

    def has_error(self) -> bool:
        """Return whether the measurement had a connection or parse error."""
        return bool(self.connection_error or self.parse_error)

    def as_dict(self) -> dict[str, Value | Entities | ErrorMessage | URL | None]:
        """Return the source measurement as dict."""
        return {
            "value": self.value,
            "total": self.total,
            "entities": self.entities[: self.MAX_ENTITIES],
            "connection_error": self.connection_error,
            "parse_error": self.parse_error,
            "api_url": self.api_url,
            "landing_url": self.landing_url,
            "source_uuid": self.source_uuid,
        }


class MetricMeasurement:
    """Class to hold measurements from one or more sources for one metric."""

    def __init__(
        self,
        source_measurements: Sequence[SourceMeasurement],
        issue_statuses: Sequence[IssueStatus],
    ) -> None:
        self.sources = source_measurements
        self.issue_statuses = issue_statuses
        self.has_error = any(source_measurement.has_error() for source_measurement in source_measurements)
        self.metric_uuid: str | None = None
        self.report_uuid: str | None = None

    def as_dict(self) -> dict:
        """Return the metric measurement as dict."""
        measurement = {
            "sources": [source_measurement.as_dict() for source_measurement in self.sources],
            "has_error": self.has_error,
            "metric_uuid": self.metric_uuid,
            "report_uuid": self.report_uuid,
        }
        if self.issue_statuses:
            measurement["issue_status"] = [issue_status.as_dict() for issue_status in self.issue_statuses]
        return measurement
