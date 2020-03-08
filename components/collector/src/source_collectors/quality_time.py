"""Collector for Quality-time."""

from functools import lru_cache
from typing import Any, Dict, List, Tuple
from urllib import parse

from collector_utilities.type import Entity, Entities, Measurement, Response, Responses, URL, Value
from .source_collector import SourceCollector


class QualityTimeMetrics(SourceCollector):
    """Collector to get the "metrics" metric from Quality-time."""

    async def _api_url(self) -> URL:
        parts = parse.urlsplit(await super()._api_url())
        netloc = f"{parts.netloc.split(':')[0]}"
        return URL(parse.urlunsplit((parts.scheme, netloc, "/api/v2", "", "")))

    async def _get_source_responses(self, api_url: URL) -> Responses:
        # First, get the report(s):
        responses = await super()._get_source_responses(URL(f"{api_url}/reports"))
        # Then, add the measurements for each of the applicable metrics:
        for _, entity in self.__get_metrics_and_entities(responses[0]):
            responses.extend(
                await super()._get_source_responses(URL(f"{api_url}/measurements/{entity['key']}")))
        return responses

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        metrics_and_entities = self.__get_metrics_and_entities(responses[0])
        entities = await self.__get_entities(responses[1:], metrics_and_entities)
        return str(len(entities)), str(len(metrics_and_entities)), entities

    async def __get_entities(
            self, responses: Responses, metrics_and_entities: List[Tuple[Dict[str, Dict], Entity]]) -> Entities:
        """Get the metric entities from the responses."""
        last_measurements = self.__get_last_measurements(responses)
        status_to_count = self._parameter("status")
        landing_url = await self._landing_url(responses)
        entities: Entities = []
        for metric, entity in metrics_and_entities:
            status, value = self.__get_status_and_value(metric, last_measurements.get(str(entity["key"]), {}))
            if status in status_to_count:
                entity["report_url"] = report_url = f"{landing_url}/{metric['report_uuid']}"
                entity["subject_url"] = f"{report_url}#{metric['subject_uuid']}"
                entity["metric_url"] = f"{report_url}#{entity['key']}"
                entity["metric"] = str(metric.get("name") or self._datamodel["metrics"][metric["type"]]["name"])
                entity["status"] = status
                unit = metric.get("unit") or self._datamodel["metrics"][metric["type"]]["unit"]
                entity["measurement"] = f"{value or '?'} {unit}"
                direction = str(metric.get("direction") or self._datamodel["metrics"][metric["type"]]["direction"])
                direction = {"<": "≦", ">": "≧"}.get(direction, direction)
                target = metric.get("target") or self._datamodel["metrics"][metric["type"]]["target"]
                entity["target"] = f"{direction} {target} {unit}"
                entities.append(entity)
        return entities

    @staticmethod
    def __get_last_measurements(responses: Responses) -> Dict[str, Measurement]:
        """Return the last measurements by metric UUID for easy lookup."""
        last_measurements = dict()
        for response in responses:
            if measurements := response.json()["measurements"]:
                last_measurement = measurements[-1]
                last_measurements[last_measurement["metric_uuid"]] = last_measurement
        return last_measurements

    @staticmethod
    def __get_status_and_value(metric, measurement: Measurement) -> Tuple[str, Value]:
        """Return the measurement value and status."""
        scale = metric.get("scale", "count")
        scale_data = measurement.get(scale, {})
        return scale_data.get("status") or "unknown", scale_data.get("value")

    @lru_cache(maxsize=2)
    def __get_metrics_and_entities(self, response: Response) -> List[Tuple[Dict[str, Dict], Entity]]:
        """Get the relevant metrics from the reports response."""
        tags = set(self._parameter("tags"))
        metric_types = self._parameter("metric_type")
        source_types = set(self._parameter("source_type"))
        metrics_and_entities = []
        for report in self.__get_reports(response):
            for subject_uuid, subject in report.get("subjects", {}).items():
                for metric_uuid, metric in subject.get("metrics", {}).items():
                    if self.__metric_is_to_be_measured(metric, metric_types, source_types, tags):
                        metric["report_uuid"] = report["report_uuid"]
                        metric["subject_uuid"] = subject_uuid
                        entity = dict(key=metric_uuid, report=report["title"], subject=subject["name"])
                        metrics_and_entities.append((metric, entity))
        return metrics_and_entities

    def __get_reports(self, response) -> List[Dict[str, Any]]:
        """Get the relevant reports from the reports response."""
        report_titles_or_ids = set(self._parameter("reports"))
        reports = list(response.json()["reports"])
        return [report for report in reports if (report_titles_or_ids & {report["title"], report["report_uuid"]})] \
            if report_titles_or_ids else reports

    @staticmethod
    def __metric_is_to_be_measured(metric, metric_types, source_types, tags) -> bool:
        """Return whether the metric has been selected by the user by means of metric type, source type or tag."""
        if tags and (tags & set(metric.get("tags", {}))) == set():
            return False
        if metric_types and metric["type"] not in metric_types:
            return False
        metric_source_types = {source["type"] for source in metric.get("sources", {}).values()}
        return not (source_types and (source_types & metric_source_types) == set())
