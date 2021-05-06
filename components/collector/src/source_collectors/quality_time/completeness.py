"""Quality-time completeness collector."""

from typing import Dict, Set
from collector_utilities.type import URL
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
        reports = await self._get_reports(reports_response)
        datamodel = await datamodel_response.json()

        entities = {}
        for report in reports:
            report_title = report["title"]
            subject_types = self.__get_subject_types(report)
            possible_metrics = self.__get_possible_metrics(datamodel, subject_types)
            actual_metrics_types = self.__get_actual_metric_types(report)

            for metric_type, entity in possible_metrics.items():
                if metric_type not in actual_metrics_types:
                    if not metric_type in entities:
                        entity["reports"] = report_title
                        entities[metric_type] = entity
                    else:
                        entities[metric_type]["reports"] = entities[metric_type]["reports"] + f", {report_title}"
        return SourceMeasurement(total=str(len(possible_metrics)), entities=list(entities.values()))

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        api_url = urls[0]
        datamodel_url = URL(f"{api_url}/api/v3/datamodel")
        reports_url = URL(f"{api_url}/api/v3/reports")
        return await super()._get_source_responses(datamodel_url, reports_url)

    def __get_subject_types(self, report):
        """Get all subject_types that are present in one report."""
        subject_types = set()
        for subject in report.get("subjects", {}).values():
            subject_types.add(subject["type"])
        
        return subject_types

    def __get_possible_metrics(self, datamodel: Dict, subject_types: Set) -> Dict:
        """Get the relevant metrics from the reports response."""
        possible_metrics = {}
        for subject_type in subject_types:
            nice_subject_name = datamodel["subjects"][subject_type]["name"]
            for metric_name in datamodel["subjects"][subject_type]["metrics"]:
                nice_metric_name = datamodel["metrics"][metric_name]["name"]
                entity = Entity(key=metric_name,
                                metric_type=nice_metric_name,
                                subject_type=nice_subject_name,
                                reports=[],
                                status="target_not_met")
                possible_metrics[metric_name] = entity

        return possible_metrics

    def __get_actual_metric_types(self, report: Dict) -> Set[str]:
        """Get the relevant metrics from the reports response."""
        metric_types = set()
        for subject in report.get("subjects", {}).values():
            for metric in subject.get("metrics", {}).values():
                metric_types.add(metric["type"])

        return metric_types
