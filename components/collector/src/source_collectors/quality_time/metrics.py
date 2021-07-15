"""Quality-time metrics collector."""

from typing import cast
from urllib import parse

from collector_utilities.type import Response, URL, Value
from model import Entities, Entity, SourceMeasurement, SourceResponses

from .base import QualityTimeCollector


Measurements = list[dict[str, dict[str, str]]]


class QualityTimeMetrics(QualityTimeCollector):
    """Collector to get the "metrics" metric from Quality-time."""

    async def _api_url(self) -> URL:
        """Extend to add the reports API path."""
        parts = parse.urlsplit(await super()._api_url())
        netloc = f"{parts.netloc.split(':')[0]}"
        return URL(parse.urlunsplit((parts.scheme, netloc, f"{parts.path}/reports", "", "")))

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Get the metric entities from the responses."""
        status_to_count = self._parameter("status")
        landing_url = await self._landing_url(responses)
        metrics_and_entities = await self.__get_metrics_and_entities(responses[0])
        entities = Entities()
        for metric, entity in metrics_and_entities:
            recent_measurements: Measurements = cast(Measurements, metric.get("recent_measurements", []))
            status, value = self.__get_status_and_value(metric, recent_measurements[-1] if recent_measurements else {})
            if status in status_to_count:
                entity["report_url"] = report_url = f"{landing_url}/{metric['report_uuid']}"
                entity["subject_url"] = f"{report_url}#{metric['subject_uuid']}"
                entity["metric_url"] = f"{report_url}#{entity['key']}"
                entity["metric"] = str(metric.get("name") or self._data_model["metrics"][metric["type"]]["name"])
                entity["status"] = status
                unit = metric.get("unit") or self._data_model["metrics"][metric["type"]]["unit"]
                entity["measurement"] = f"{value or '?'} {unit}"
                direction = str(metric.get("direction") or self._data_model["metrics"][metric["type"]]["direction"])
                direction = {"<": "≦", ">": "≧"}.get(direction, direction)
                target = metric.get("target") or self._data_model["metrics"][metric["type"]]["target"]
                entity["target"] = f"{direction} {target} {unit}"
                entities.append(entity)
        return SourceMeasurement(total=str(len(metrics_and_entities)), entities=entities)

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
                        entity = Entity(key=metric_uuid, report=report["title"], subject=subject["name"])
                        metrics_and_entities.append((metric, entity))
        return metrics_and_entities

    @staticmethod
    def __metric_is_to_be_measured(metric, metric_types, source_types, tags) -> bool:
        """Return whether the metric has been selected by the user by means of metric type, source type or tag."""
        if tags and (tags & set(metric.get("tags", {}))) == set():
            return False
        if metric_types and metric["type"] not in metric_types:
            return False
        metric_source_types = {source["type"] for source in metric.get("sources", {}).values()}
        return not (source_types and (source_types & metric_source_types) == set())
