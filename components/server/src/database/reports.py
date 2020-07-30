"""Reports collection."""

from dataclasses import dataclass
from typing import cast, Any, Dict, List, Union

import pymongo
from pymongo.database import Database

from server_utilities.functions import iso_timestamp, unique
from server_utilities.type import Change, MetricId, ReportId, SourceId, SubjectId
from model.queries import get_metric_uuid, get_report_uuid, get_subject_uuid
from .datamodels import latest_datamodel


TIMESTAMP_DESCENDING = [("timestamp", pymongo.DESCENDING)]


def latest_reports(database: Database, max_iso_timestamp: str = ""):
    """Return the latest, undeleted, reports in the reports collection."""
    for report_uuid in database.reports.distinct("report_uuid"):
        report = database.reports.find_one(
            filter={"report_uuid": report_uuid, "timestamp": {"$lt": max_iso_timestamp or iso_timestamp()}},
            sort=TIMESTAMP_DESCENDING)
        if report and "deleted" not in report:
            report["_id"] = str(report["_id"])
            yield report


def latest_reports_overview(database: Database, max_iso_timestamp: str = "") -> Dict:
    """Return the latest reports overview."""
    timestamp_filter = dict(timestamp={"$lt": max_iso_timestamp or iso_timestamp()})
    overview = database.reports_overviews.find_one(timestamp_filter, sort=TIMESTAMP_DESCENDING)
    if overview:  # pragma: no cover-behave
        overview["_id"] = str(overview["_id"])
    return overview or dict()


def report_exists(database: Database, report_uuid: ReportId):
    """Return whether a report with the specified report uuid exists."""
    return report_uuid in database.reports.distinct("report_uuid")


def latest_metric(database: Database, metric_uuid: MetricId):
    """Return the latest metric with the specified metric uuid."""
    for report in latest_reports(database):
        for subject in report.get("subjects", {}).values():
            metrics = subject.get("metrics", {})
            if metric_uuid in metrics:
                return metrics[metric_uuid]
    return None


def insert_new_report(database: Database, *reports) -> Dict[str, Any]:
    """Insert one or more new reports in the reports collection."""
    _prepare_documents_for_insertion(*reports, last=True)
    report_uuids = [report["report_uuid"] for report in reports]
    database.reports.update_many(
        {"report_uuid": {"$in": report_uuids}, "last": {"$exists": True}}, {"$unset": {"last": ""}})
    if len(reports) > 1:
        database.reports.insert_many(reports, ordered=False)
    else:
        database.reports.insert(reports[0])
    return dict(ok=True)


def insert_new_reports_overview(database: Database, reports_overview) -> Dict[str, Any]:
    """Insert a new reports overview in the reports overview collection."""
    _prepare_documents_for_insertion(reports_overview)
    database.reports_overviews.insert(reports_overview)
    return dict(ok=True)


def _prepare_documents_for_insertion(*documents, **extra_attributes) -> None:
    """Prepare the documents for insertion in the database by removing any ids and setting the extra attributes."""
    now = iso_timestamp()
    for document in documents:
        if "_id" in document:
            del document["_id"]
        document["timestamp"] = now
        for key, value in extra_attributes.items():
            document[key] = value


def changelog(database: Database, nr_changes: int, **uuids):
    """Return the changelog, narrowed to a single report, subject, metric, or source if so required.
    The uuids keyword arguments may contain report_uuid="report_uuid", and one of subject_uuid="subject_uuid",
    metric_uuid="metric_uuid", and source_uuid="source_uuid"."""
    projection = {"delta.description": True, "delta.email": True, "timestamp": True}
    delta_filter: Dict[str, Union[Dict, List]] = {"delta": {"$exists": True}}
    changes: List[Change] = []
    if not uuids:
        changes.extend(database.reports_overviews.find(
            filter=delta_filter, sort=TIMESTAMP_DESCENDING, limit=nr_changes*2, projection=projection))
    old_report_delta_filter = {f"delta.{key}": value for key, value in uuids.items() if value}
    new_report_delta_filter = {"delta.uuids": {"$in": list(uuids.values())}}
    delta_filter["$or"] = [old_report_delta_filter, new_report_delta_filter]
    changes.extend(database.reports.find(
        filter=delta_filter, sort=TIMESTAMP_DESCENDING, limit=nr_changes*2, projection=projection))
    changes = sorted(changes, reverse=True, key=lambda change: change["timestamp"])
    # Weed out potential duplicates, because when a user moves items between reports both reports get the same delta
    return list(unique(changes, lambda change: cast(Dict[str, str], change["delta"])["description"]))[:nr_changes]


@dataclass
class Data:
    """Class to hold all data relevant to a specific report, subject, metric or source."""
    def __init__(self, database: Database) -> None:
        self.datamodel = latest_datamodel(database)
        self.reports = list(latest_reports(database))
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
    def __init__(self, database: Database, report_uuid: ReportId = None, subject_uuid: SubjectId = None) -> None:
        self.report_uuid = report_uuid
        self.subject_uuid = subject_uuid
        super().__init__(database)

    def get_uuid(self) -> None:
        self.report_uuid = get_report_uuid(self.reports, self.subject_uuid) if self.subject_uuid else self.report_uuid
        super().get_uuid()

    def get_data(self) -> None:
        super().get_data()
        self.report = list(filter(lambda report: self.report_uuid == report["report_uuid"], self.reports))[0]
        self.report_name = self.report.get("title") or ""


class SubjectData(ReportData):
    """Class to hold data about a specific subject."""
    def __init__(self, database: Database, subject_uuid: SubjectId = None, metric_uuid: MetricId = None) -> None:
        self.subject_uuid = subject_uuid
        self.metric_uuid = metric_uuid
        super().__init__(database, subject_uuid=subject_uuid)

    def get_uuid(self) -> None:
        self.subject_uuid = get_subject_uuid(self.reports, self.metric_uuid) if self.metric_uuid else self.subject_uuid
        super().get_uuid()

    def get_data(self) -> None:
        super().get_data()
        self.subject = self.report["subjects"][self.subject_uuid] if self.subject_uuid else {}
        self.subject_name = self.name("subject")


class MetricData(SubjectData):
    """Class to hold data about a specific metric."""
    def __init__(self, database: Database, metric_uuid: MetricId = None, source_uuid: SourceId = None) -> None:
        self.metric_uuid = metric_uuid
        self.source_uuid = source_uuid
        super().__init__(database, metric_uuid=metric_uuid)

    def get_uuid(self) -> None:
        self.metric_uuid = get_metric_uuid(self.reports, self.source_uuid) if self.source_uuid else self.metric_uuid
        super().get_uuid()

    def get_data(self) -> None:
        super().get_data()
        self.metric = self.subject["metrics"][self.metric_uuid] if self.metric_uuid else {}
        self.metric_name = self.name("metric")


class SourceData(MetricData):
    """Class to hold data about a specific source."""
    def __init__(self, database: Database, source_uuid: SourceId) -> None:
        self.source_uuid = source_uuid
        super().__init__(database, source_uuid=source_uuid)

    def get_data(self) -> None:
        super().get_data()
        self.source = self.metric["sources"][self.source_uuid]
        self.source_name = self.name("source")
