"""Collector for Quality-time."""

from datetime import datetime
from typing import Any, Dict, List, Tuple, cast
from urllib import parse

from dateutil.parser import parse as parse_datetime

from base_collectors import SourceCollector, SourceCollectorException, SourceUpToDatenessCollector
from collector_utilities.type import URL, Response, Value
from source_model import Entity, SourceMeasurement, SourceResponses


Measurements = List[Dict[str, Dict[str, str]]]


class QualityTimeCollector(SourceCollector):
    """Base collector for Quality-time metrics."""

    async def _api_url(self) -> URL:
        parts = parse.urlsplit(await super()._api_url())
        netloc = f"{parts.netloc.split(':')[0]}"
        return URL(parse.urlunsplit((parts.scheme, netloc, "/api/v3/reports", "", "")))

    async def _get_reports(self, response: Response) -> List[Dict[str, Any]]:
        """Get the relevant reports from the reports response."""
        report_titles_or_ids = set(self._parameter("reports"))
        reports = list((await response.json())["reports"])
        reports = (
            [report for report in reports if (report_titles_or_ids & {report["title"], report["report_uuid"]})]
            if report_titles_or_ids
            else reports
        )
        if not reports:
            message = "No reports found" + (f" with title or id {report_titles_or_ids}" if report_titles_or_ids else "")
            raise SourceCollectorException(message)
        return reports


class QualityTimeMetrics(QualityTimeCollector):
    """Collector to get the "metrics" metric from Quality-time."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Get the metric entities from the responses."""
        status_to_count = self._parameter("status")
        landing_url = await self._landing_url(responses)
        metrics_and_entities = await self.__get_metrics_and_entities(responses[0])
        entities: List[Entity] = []
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
    def __get_status_and_value(metric, measurement) -> Tuple[str, Value]:
        """Return the measurement value and status."""
        scale = metric.get("scale", "count")
        scale_data = measurement.get(scale, {})
        return scale_data.get("status") or "unknown", scale_data.get("value")

    async def __get_metrics_and_entities(self, response: Response) -> List[Tuple[Dict[str, Measurements], Entity]]:
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


class QualityTimeSourceUpToDateness(QualityTimeCollector, SourceUpToDatenessCollector):
    """Collector to get the "source up-to-dateness" metric from Quality-time."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        measurement_dates = []
        for report in await self._get_reports(response):
            for subject in report.get("subjects", {}).values():
                for metric in subject.get("metrics", {}).values():
                    if recent_measurements := metric.get("recent_measurements", []):
                        measurement_dates.append(parse_datetime(recent_measurements[-1]["end"]))
        return min(measurement_dates, default=datetime.min)
