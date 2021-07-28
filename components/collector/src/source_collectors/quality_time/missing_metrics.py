"""Quality-time missing metrics collector."""

from typing import cast

from collector_utilities.type import URL
from model import SourceMeasurement, SourceResponses
from model.entity import Entities, Entity

from .base import QualityTimeCollector


class QualityTimeMissingMetrics(QualityTimeCollector):
    """Collector to get the number of missing metrics from Quality-time."""

    async def _get_source_responses(self, *urls: URL, **kwargs) -> SourceResponses:
        """Get responses for reports and the datamodel."""
        api_url = urls[0]
        datamodel_url = URL(f"{api_url}/datamodel")
        reports_url = URL(f"{api_url}/reports")
        return await super()._get_source_responses(datamodel_url, reports_url, **kwargs)

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Get the metric entities from the responses."""
        datamodel_response, reports_response = responses
        data_model = await datamodel_response.json()
        reports = await self._get_reports(reports_response)
        landing_url = await self._landing_url(responses)
        total = self.__nr_of_possible_metric_types(data_model, reports)
        entities = self.__missing_metric_type_entities(data_model, reports, landing_url)
        return SourceMeasurement(total=str(total), entities=entities)

    def __nr_of_possible_metric_types(self, data_model: dict, reports: list[dict]) -> int:
        """Return the number of possible metric types in the reports."""
        return sum(self.__report_nr_of_possible_metric_types(data_model, report) for report in reports)

    def __report_nr_of_possible_metric_types(self, data_model: dict, report: dict) -> int:
        """Return the number of possible metric types in the report."""
        subjects = report.get("subjects", {}).values()
        return sum(len(self.__subject_possible_metric_types(data_model, subject)) for subject in subjects)

    def __missing_metric_type_entities(self, data_model: dict, reports: list[dict], landing_url: URL) -> Entities:
        """Return the reports' missing metric types as entities."""
        entities = Entities()
        for report in reports:
            entities.extend(self.__report_missing_metric_type_entities(data_model, report, landing_url))
        return entities

    def __report_missing_metric_type_entities(self, data_model: dict, report: dict, landing_url: URL) -> Entities:
        """Return the report's missing metric types as entities."""
        entities = Entities()
        for subject_uuid in report.get("subjects", {}):
            entities.extend(self.__subject_missing_metric_type_entities(data_model, report, subject_uuid, landing_url))
        return entities

    def __subject_missing_metric_type_entities(
        self, data_model: dict, report: dict, subject_uuid: str, landing_url: URL
    ) -> Entities:
        """Return the subject's missing metric types as entities."""
        report_uuid = report["report_uuid"]
        report_url = f"{landing_url}/{report_uuid}"
        subject = report["subjects"][subject_uuid]
        subject_type_name = data_model["subjects"][subject["type"]]["name"]
        return Entities(
            Entity(
                key=f"{report_uuid}:{subject_uuid}:{metric_type}",
                report=report["title"],
                report_url=report_url,
                subject=subject.get("name", subject_type_name),
                subject_url=f"{report_url}#{subject_uuid}",
                subject_type=subject_type_name,
                metric_type=data_model["metrics"][metric_type]["name"],
            )
            for metric_type in self.__subject_missing_metric_types(data_model, subject)
        )

    def __subject_missing_metric_types(self, data_model: dict, subject: dict) -> list[str]:
        """Return the subject's missing metric types."""
        possible_types = self.__subject_possible_metric_types(data_model, subject)
        actual_types = set(metric["type"] for metric in subject.get("metrics", {}).values())
        return [metric_type for metric_type in possible_types if metric_type not in actual_types]

    @staticmethod
    def __subject_possible_metric_types(data_model: dict, subject: dict) -> list[str]:
        """Return the subject's possible metric types."""
        return cast(list[str], data_model["subjects"][subject["type"]]["metrics"])
