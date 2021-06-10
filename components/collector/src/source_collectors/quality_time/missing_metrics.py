"""Quality-time completeness collector."""

from typing import Dict, Set
from collector_utilities.type import URL
from source_model import SourceMeasurement, SourceResponses
from source_model.entity import Entities, Entity

from .base import QualityTimeCollector


Measurements = list[dict[str, dict[str, str]]]


class QualityTimeMissingMetrics(QualityTimeCollector):
    """Collector to get the "completeness" metric from Quality-time."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Get the metric entities from the responses."""
        datamodel_response, reports_response = responses
        datamodel = await datamodel_response.json()
        reports = await self._get_reports(reports_response)

        entity_dict = {}
        for report in reports:
            report_title = report["title"]
            subject_types = {subject["type"] for subject in report.get("subjects", {}).values()}
            possible_metrics = self.__get_possible_metrics(datamodel, subject_types)
            actual_metrics_types = self.__get_actual_metric_types(report)

            for metric_type, entity in possible_metrics.items():
                if metric_type not in actual_metrics_types:
                    if metric_type not in entity_dict:
                        entity["reports"] = report_title
                        entity_dict[metric_type] = entity
                    else:
                        entity_dict[metric_type]["reports"] = entity_dict[metric_type]["reports"] + f", {report_title}"

        entities = Entities(list(entity_dict.values()))
        return SourceMeasurement(total=str(len(possible_metrics)), entities=entities)

    async def _get_source_responses(self, *urls: URL, **kwargs) -> SourceResponses:
        """Get responses for reports and the datamodel."""
        api_url = urls[0]
        datamodel_url = URL(f"{api_url}/datamodel")
        reports_url = URL(f"{api_url}/reports")
        return await super()._get_source_responses(datamodel_url, reports_url, **kwargs)

    @staticmethod
    def __get_possible_metrics(datamodel: Dict, subject_types: Set) -> Dict:
        """Get the relevant metrics from the reports response."""
        possible_metrics = {}
        for subject_type in subject_types:
            subject_name = datamodel["subjects"][subject_type]["name"]
            for metric_type in datamodel["subjects"][subject_type]["metrics"]:
                metric_name = datamodel["metrics"][metric_type]["name"]
                entity = Entity(
                    key=metric_type,
                    metric_type=metric_name,
                    subject_type=subject_name,
                    reports=[],
                )
                possible_metrics[metric_type] = entity

        return possible_metrics

    @staticmethod
    def __get_actual_metric_types(report: Dict) -> Set[str]:
        """Get the relevant metrics from the reports response."""
        metric_types = set()
        for subject in report.get("subjects", {}).values():
            for metric in subject.get("metrics", {}).values():
                metric_types.add(metric["type"])

        return metric_types
