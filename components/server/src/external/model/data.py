"""Reports collection."""

from dataclasses import dataclass
from typing import Any, cast

from shared.utils.type import MetricId, ReportId, SubjectId


@dataclass
class Data:
    """Class to hold all data relevant to a specific report, subject, metric or source."""

    def __init__(self, data_model, reports) -> None:
        self.datamodel = data_model
        self.reports = reports

    def name(self, entity: str) -> str:
        """Return the name of the entity."""
        instance = getattr(self, entity)
        return instance.get("name") or str(self.datamodel[f"{entity}s"][instance["type"]]["name"])


class ReportData(Data):
    """Class to hold data about a specific report."""

    def __init__(self, data_model, reports, report_uuid: ReportId = None, subject_uuid: SubjectId = None) -> None:
        self.report_uuid = self.get_report_uuid(reports, subject_uuid) if subject_uuid else report_uuid
        super().__init__(data_model, reports)
        self.report = list(filter(lambda report: self.report_uuid == report["report_uuid"], reports))[0]
        self.report_name = self.report.get("title") or ""

    @staticmethod
    def get_report_uuid(reports, subject_uuid: SubjectId) -> ReportId:
        """Find the uuid of the report that contains a subject with the given subject uuid."""
        report = [report for report in reports if subject_uuid in report["subjects"]][0]
        return cast(ReportId, report["report_uuid"])
