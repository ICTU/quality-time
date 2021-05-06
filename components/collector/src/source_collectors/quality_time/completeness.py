"""Quality-time completeness collector."""

from collector_utilities.type import Response, URL
from source_model import SourceMeasurement, SourceResponses
from source_model.entity import Entity

from .base import QualityTimeCollector


Measurements = list[dict[str, dict[str, str]]]


class QualityTimeCompleteness(QualityTimeCollector):
    """Collector to get the "completeness" metric from Quality-time."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Get the metric entities from the responses."""
        datamodel_response = responses[0]
        reports_response = responses[1]
        possible_metrics = await self.__get_possible_metrics(datamodel_response, reports_response)
        actual_metrics = await self.__get_actual_metrics(datamodel_response, reports_response)
        entities = [entity for key, entity in possible_metrics.items() if key not in actual_metrics]
        return SourceMeasurement(total=str(len(possible_metrics)), entities=entities)

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        api_url = urls[0]
        datamodel_url = URL(f"{api_url}/api/v3/datamodel")
        reports_url = URL(f"{api_url}/api/v3/reports")
        return await super()._get_source_responses(datamodel_url, reports_url)

    async def __get_possible_metrics(self, datamodel_response: Response, reports_response: Response) -> list[str]:
        """Get the relevant metrics from the reports response."""
        subject_types = set()
        for report in await self._get_reports(reports_response):
            for subject in report.get("subjects", {}).values():
                subject_types.add(subject["type"])

        datamodel = await datamodel_response.json()
        possible_metrics = {}
        for subject_type in subject_types:
            nice_subject_name = datamodel["subjects"][subject_type]["name"]
            for metric_name in datamodel["subjects"][subject_type]["metrics"]:
                nice_metric_name = datamodel["metrics"][metric_name]["name"]
                entity = Entity(key=metric_name, metric_type=nice_metric_name, subject_type=nice_subject_name, status="target_not_met")
                possible_metrics[metric_name] = entity
        return possible_metrics

    async def __get_actual_metrics(self, datamodel_response: Response, reports_response: Response) -> list[str]:
        """Get the relevant metrics from the reports response."""
        datamodel = await datamodel_response.json()
        entities = {}
        for report in await self._get_reports(reports_response):
            for subject in report.get("subjects", {}).values():
                for metric in subject.get("metrics", {}).values():
                    nice_metric_name = datamodel["metrics"][metric["type"]]["name"]
                    nice_subject_name = datamodel["subjects"][subject["type"]]["name"]
                    entity = Entity(key=metric["type"], metric_type=nice_metric_name, subject_type=nice_subject_name, status="target_met")
                    entities[metric["type"]] = entity

        return entities
