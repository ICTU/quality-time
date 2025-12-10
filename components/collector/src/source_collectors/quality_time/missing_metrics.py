"""Quality-time missing metrics collector."""

from typing import TYPE_CHECKING

from collector_utilities.functions import match_string_or_regular_expression
from collector_utilities.type import URL
from model import SourceMeasurement, SourceResponses
from model.entity import Entities, Entity

from .base import QualityTimeCollector

if TYPE_CHECKING:
    from shared.utils.type import ReportId


class QualityTimeMissingMetrics(QualityTimeCollector):
    """Collector to get the number of missing metrics from Quality-time."""

    async def _api_url(self) -> URL:
        """Extend to add the reports API path."""
        return URL(await super()._api_url() + "/api/internal")

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Get responses for reports and the datamodel."""
        api_url = urls[0]
        datamodel_url = URL(f"{api_url}/datamodel")
        reports_url = URL(f"{api_url}/report")
        return await super()._get_source_responses(datamodel_url, reports_url)

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Get the metric entities from the responses."""
        datamodel_response, reports_response = responses
        self.data_model = await datamodel_response.json()
        self.reports = await self._get_reports(reports_response)
        landing_url = await self._landing_url(responses)
        total = self.__nr_of_possible_metric_types(self.data_model, self.reports)
        entities = self.__missing_metric_type_entities(self.data_model, self.reports, landing_url)
        included_entities = Entities(entity for entity in entities if self._include_entity(entity))
        return SourceMeasurement(total=str(total), entities=included_entities)

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include the entity in the measurement."""
        metric_type = entity["metric_type"]
        metric_source_types = set(self.data_model["metrics"][metric_type]["sources"])

        source_types_to_include = set(self._parameter("source_types_to_include"))
        if not (source_types_to_include & metric_source_types):
            return False

        source_types_to_ignore = set(self._parameter("source_types_to_ignore"))
        if metric_source_types - source_types_to_ignore == set():
            return False

        metric_types_to_ignore = self._parameter("metric_types_to_ignore_when_used_at_least_once")
        if metric_type in metric_types_to_ignore and metric_type in self.__used_metric_types(entity["report_uuid"]):
            return False

        subjects_to_include = self._parameter("subjects_to_include")
        if subjects_to_include and not self.__subject_matches(entity, subjects_to_include):
            return False

        subjects_to_ignore = self._parameter("subjects_to_ignore")
        if subjects_to_ignore and self.__subject_matches(entity, subjects_to_ignore):  # noqa: SIM103
            return False

        return True

    def __subject_matches(self, entity: Entity, subjects_to_match: list[str] | str) -> bool:
        """Return whether the entity's subject matches the subjects to match by name or UUID."""
        subject_name_matches = match_string_or_regular_expression(entity["subject"], subjects_to_match)
        subject_uuid_matches = match_string_or_regular_expression(entity["subject_uuid"], subjects_to_match)
        return subject_name_matches or subject_uuid_matches

    def __nr_of_possible_metric_types(self, data_model: dict, reports: list[dict]) -> int:
        """Return the number of possible metric types in the reports."""
        return sum(self.__report_nr_of_possible_metric_types(data_model, report) for report in reports)

    def __report_nr_of_possible_metric_types(self, data_model: dict, report: dict) -> int:
        """Return the number of possible metric types in the report."""
        subjects = report.get("subjects", {}).values()
        return sum(len(self.supported_metric_types(data_model, subject)) for subject in subjects)

    def __missing_metric_type_entities(self, data_model: dict, reports: list[dict], landing_url: URL) -> Entities:
        """Return the reports' missing metric types as entities."""
        entities = Entities()
        for report in reports:
            entities.extend(self.__report_missing_metric_type_entities(data_model, report, landing_url))
        return entities

    def __used_metric_types(self, report_uuid: ReportId) -> set[str]:
        """Return the metric types used in the report with the given report UUID."""
        metric_types = set()
        report = next(report for report in self.reports if report["report_uuid"] == report_uuid)
        for subject in report.get("subjects", {}).values():
            for metric in subject.get("metrics", {}).values():
                metric_types.add(metric["type"])
        return metric_types

    def __report_missing_metric_type_entities(self, data_model: dict, report: dict, landing_url: URL) -> Entities:
        """Return the report's missing metric types as entities."""
        entities = Entities()
        for subject_uuid in report.get("subjects", {}):
            entities.extend(self.__subject_missing_metric_type_entities(data_model, report, subject_uuid, landing_url))
        return entities

    def __subject_missing_metric_type_entities(
        self,
        data_model: dict,
        report: dict,
        subject_uuid: str,
        landing_url: URL,
    ) -> Entities:
        """Return the subject's missing metric types as entities."""
        report_uuid = report["report_uuid"]
        report_url = f"{landing_url}/{report_uuid}"
        subject = report["subjects"][subject_uuid]
        subject_type = self.subject_type(data_model["subjects"], subject["type"])
        subject_type_name = subject_type["name"]
        return Entities(
            Entity(
                key=f"{report_uuid}:{subject_uuid}:{metric_type}",
                report=report["title"],
                report_uuid=report_uuid,
                report_url=report_url,
                subject=subject.get("name") or subject_type_name,
                subject_url=f"{report_url}#{subject_uuid}",
                subject_uuid=f"{subject_uuid}",
                subject_type=subject_type_name,
                subject_type_url=subject_type["reference_documentation_url"],
                metric_type=metric_type,
                metric_type_name=data_model["metrics"][metric_type]["name"],
                metric_type_url=data_model["metrics"][metric_type]["reference_documentation_url"],
                source_types=self.supporting_source_types(data_model, metric_type),
            )
            for metric_type in self.__missing_metric_types(data_model, subject)
        )

    def __missing_metric_types(self, data_model: dict, subject: dict) -> list[str]:
        """Return the subject's supported metric types minus the used metric types."""
        supported_metric_types = self.supported_metric_types(data_model, subject)
        actual_types = {metric["type"] for metric in subject.get("metrics", {}).values()}
        return [metric_type for metric_type in supported_metric_types if metric_type not in actual_types]

    @classmethod
    def supported_metric_types(cls, data_model: dict, subject: dict) -> list[str]:
        """Return the subject's supported metric types."""
        subject_type = cls.subject_type(data_model["subjects"], subject["type"])
        metric_types = set(subject_type.get("metrics", []))
        for child_subject in subject_type.get("subjects", {}).values():
            metric_types |= set(child_subject.get("metrics", []))
        return sorted(metric_types)

    @classmethod
    def subject_type(cls, subjects: dict[str, dict], subject_type_name: str) -> dict:
        """Return the subject type with the specified name."""
        for name, subject_type in subjects.items():
            if subject_type_name == name:
                return subject_type
            if composite_subject_type := cls.subject_type(subject_type.get("subjects", {}), subject_type_name):
                return composite_subject_type
        return {}

    @staticmethod
    def supporting_source_types(data_model: dict, metric_type: str) -> str:
        """Return a comma-separated list of names of source types that support the given metric type."""
        source_types = data_model["metrics"][metric_type]["sources"]
        return ", ".join(sorted([data_model["sources"][source_type]["name"] for source_type in source_types]))
