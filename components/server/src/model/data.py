"""Reports collection."""

from dataclasses import dataclass

from server_utilities.type import MetricId, ReportId, SourceId, SubjectId
from model.queries import get_metric_uuid, get_report_uuid, get_subject_uuid


@dataclass
class Data:
    """Class to hold all data relevant to a specific report, subject, metric or source."""
    def __init__(self, data_model, reports) -> None:
        self.datamodel = data_model
        self.reports = reports
        self.get_uuid()
        self.get_data()

    def get_uuid(self) -> None:
        """Determine the UUID of the entity."""

    def get_data(self) -> None:
        """Get the data."""

    def name(self, entity: str) -> str:
        """Return the name of the entity."""
        instance = getattr(self, entity)
        return instance.get("name") or str(self.datamodel[f"{entity}s"][instance["type"]]["name"])


class ReportData(Data):
    """Class to hold data about a specific report."""
    def __init__(self, data_model, reports, report_uuid: ReportId = None, subject_uuid: SubjectId = None) -> None:
        self.report_uuid = report_uuid
        self.subject_uuid = subject_uuid
        super().__init__(data_model, reports)

    def get_uuid(self) -> None:
        self.report_uuid = get_report_uuid(self.reports, self.subject_uuid) if self.subject_uuid else self.report_uuid
        super().get_uuid()

    def get_data(self) -> None:
        super().get_data()
        self.report = list(filter(lambda report: self.report_uuid == report["report_uuid"], self.reports))[0]
        self.report_name = self.report.get("title") or ""


class SubjectData(ReportData):
    """Class to hold data about a specific subject."""
    def __init__(self, data_model, reports, subject_uuid: SubjectId = None, metric_uuid: MetricId = None) -> None:
        self.subject_uuid = subject_uuid
        self.metric_uuid = metric_uuid
        super().__init__(data_model, reports, subject_uuid=subject_uuid)

    def get_uuid(self) -> None:
        self.subject_uuid = get_subject_uuid(self.reports, self.metric_uuid) if self.metric_uuid else self.subject_uuid
        super().get_uuid()

    def get_data(self) -> None:
        super().get_data()
        self.subject = self.report["subjects"][self.subject_uuid] if self.subject_uuid else {}
        self.subject_name = self.name("subject")


class MetricData(SubjectData):
    """Class to hold data about a specific metric."""
    def __init__(self, data_model, reports, metric_uuid: MetricId = None, source_uuid: SourceId = None) -> None:
        self.metric_uuid = metric_uuid
        self.source_uuid = source_uuid
        super().__init__(data_model, reports, metric_uuid=metric_uuid)

    def get_uuid(self) -> None:
        self.metric_uuid = get_metric_uuid(self.reports, self.source_uuid) if self.source_uuid else self.metric_uuid
        super().get_uuid()

    def get_data(self) -> None:
        super().get_data()
        self.metric = self.subject["metrics"][self.metric_uuid] if self.metric_uuid else {}
        self.metric_name = self.name("metric")


class SourceData(MetricData):
    """Class to hold data about a specific source."""
    def __init__(self, data_model, reports, source_uuid: SourceId) -> None:
        self.source_uuid = source_uuid
        super().__init__(data_model, reports, source_uuid=source_uuid)

    def get_data(self) -> None:
        super().get_data()
        self.source = self.metric["sources"][self.source_uuid]
        self.source_name = self.name("source")
