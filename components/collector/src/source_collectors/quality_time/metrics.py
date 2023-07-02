"""Quality-time metrics collector."""

from datetime import datetime
from typing import cast
from urllib import parse

from shared.utils.date_time import now
from shared_data_model import DATA_MODEL

from collector_utilities.date_time import parse_datetime
from collector_utilities.type import URL, Response, Value
from model import Entities, Entity, SourceMeasurement, SourceResponses

from .base import QualityTimeCollector

Measurements = list[dict[str, dict[str, str]]]


class QualityTimeMetrics(QualityTimeCollector):
    """Collector to get the "metrics" metric from Quality-time."""

    async def _api_url(self) -> URL:
        """Extend to add the reports API path."""
        parts = parse.urlsplit(await super()._api_url())
        netloc = f"{parts.netloc.split(':')[0]}"
        return URL(parse.urlunsplit((parts.scheme, netloc, f"{parts.path}/report", "", "")))

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Get the metric entities from the responses."""
        landing_url = await self._landing_url(responses)
        metrics_and_entities = await self.__get_metrics_and_entities(responses[0])
        parsed_entities = [self.__parse_entity(entity, metric, landing_url) for metric, entity in metrics_and_entities]
        entities = Entities([entity for entity in parsed_entities if self._include_entity(entity)])
        return SourceMeasurement(total=str(len(metrics_and_entities)), entities=entities)

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include the entity in the measurement."""
        if entity["status"] not in self._parameter("status"):
            return False
        min_status_duration = int(cast(int, self._parameter("min_status_duration") or 0))
        status_start = self.__metric_status_start(entity["status_start_date"])
        if not status_start and min_status_duration > 0:
            return False
        if status_start and (now() - status_start).days < min_status_duration:
            return False
        return True

    @staticmethod
    def __get_status_and_value(metric, measurement) -> tuple[str, Value]:
        """Return the measurement value and status."""
        scale = metric.get("scale", "count")
        scale_data = measurement.get(scale, {})
        return scale_data.get("status") or "unknown", scale_data.get("value")

    async def __get_metrics_and_entities(self, response: Response) -> list[tuple[dict[str, Measurements], Entity]]:
        """Get the relevant metrics from the reports response."""
        tags = set(self._parameter("tags"))
        metric_types = self._parameter("metric_type")
        source_types = set(self._parameter("source_type"))
        metrics_and_entities = []
        for report in await self._get_reports(response):
            for subject_uuid, subject in report.get("subjects", {}).items():
                for metric_uuid, metric in subject.get("metrics", {}).items():
                    if self.__metric_is_to_be_measured(metric, metric_types, source_types, tags):
                        metric["report_uuid"] = report["report_uuid"]
                        metric["subject_uuid"] = subject_uuid
                        subject_name = str(subject.get("name") or DATA_MODEL.subjects[subject["type"]].name)
                        entity = Entity(key=metric_uuid, report=report["title"], subject=subject_name)
                        metrics_and_entities.append((metric, entity))
        return metrics_and_entities

    def __parse_entity(self, entity: Entity, metric, landing_url: URL) -> Entity:
        """Update the entity attributes."""
        recent_measurements: Measurements = cast(Measurements, metric.get("recent_measurements", []))
        status, value = self.__get_status_and_value(metric, recent_measurements[-1] if recent_measurements else {})
        entity["report_url"] = report_url = f"{landing_url}/{metric['report_uuid']}"
        entity["subject_url"] = f"{report_url}#{metric['subject_uuid']}"
        entity["metric_url"] = f"{report_url}#{entity['key']}"
        entity["metric"] = str(metric.get("name") or DATA_MODEL.metrics[metric["type"]].name)
        entity["status"] = status
        status_start = self.__metric_status_start(metric.get("status_start", ""))
        entity["status_start_date"] = status_start.isoformat() if status_start else ""
        entity["unit"] = metric.get("unit") or DATA_MODEL.metrics[metric["type"]].unit.value
        entity["measurement"] = value
        direction = str(metric.get("direction") or DATA_MODEL.metrics[metric["type"]].direction.value)
        direction = {"<": "≦", ">": "≧"}.get(direction, direction)
        target = metric.get("target") or DATA_MODEL.metrics[metric["type"]].target
        entity["target"] = f"{direction} {target}"
        return entity

    @staticmethod
    def __metric_is_to_be_measured(metric, metric_types, source_types, tags) -> bool:
        """Return whether the metric has been selected by the user by means of metric type, source type or tag."""
        if tags and (tags & set(metric.get("tags", {}))) == set():
            return False
        if metric_types and metric["type"] not in metric_types:
            return False
        metric_source_types = {source["type"] for source in metric.get("sources", {}).values()}
        return not (source_types and (source_types & metric_source_types) == set())

    @staticmethod
    def __metric_status_start(status_start: str) -> None | datetime:
        """Return the status start date/time of the metric."""
        return parse_datetime(status_start) if status_start else None
