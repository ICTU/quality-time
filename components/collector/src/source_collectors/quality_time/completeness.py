"""Quality-time completeness collector."""

from typing import cast

from collector_utilities.type import Response, Value
from source_model import Entities, Entity, SourceMeasurement, SourceResponses

from .base import QualityTimeCollector


Measurements = list[dict[str, dict[str, str]]]


class QualityTimeCompleteness(QualityTimeCollector):
    """Collector to get the "completeness" metric from Quality-time."""

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

    async def __get_possible_metrics(self, datamodel_response: Response, reports_response: Response) -> list[str]:
        """Get the relevant metrics from the reports response."""
        subject_types = set()
        for report in await self._get_reports(reports_response):
            for subject in report.get("subjects", {}).values():
                subject_types.add(subject["type"])

        possible_metrics = set()
        for subject_type in subject_types:
            possible_metrics += datamodel_response["subjects"][subject_type]["metrics"]
        return possible_metrics

    async def __get_actual_metrics(self, datamodel_response: Response, reports_response: Response) -> list[str]:
        """Get the relevant metrics from the reports response."""
        metrics = set()
        for report in await self._get_reports(reports_response):
            for subject in report.get("subjects", {}).values():
                for metric in subject.get("metrics", {}).values():
                    metrics.add(metric)

        return metrics
