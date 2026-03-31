"""Database migrations."""

from typing import TYPE_CHECKING

from utils.log import get_logger

if TYPE_CHECKING:
    from pymongo.database import Database
    from pymongo.collection import Collection


def perform_migrations(database: Database) -> None:
    """Perform the database migrations."""
    logger = get_logger()
    for report in database.reports.find(filter={"last": True, "deleted": {"$exists": False}}):
        report_uuid = report["report_uuid"]
        logger.info("Checking report %s for necessary updates", report_uuid)
        changes = [
            change
            for change in (
                remove_metric_addition(report),
                remove_checkmarx(report),
                remove_subject_description(report),
            )
            if change
        ]
        if any(changes):
            logger.info("Updating report %s to %s", report_uuid, " and ".join(change for change in changes if change))
            replace_document(database.reports, report)


def remove_metric_addition(report) -> str:
    """Remove the addition field from all metrics."""
    # Added after Quality-time v5.47.1, see https://github.com/ICTU/quality-time/issues/12142
    change_description = ""
    for metric in metrics(report):
        if "addition" in metric:
            change_description = "remove the addition field from metrics"
            del metric["addition"]
    return change_description


def remove_checkmarx(report) -> str:
    """Remove the Checkmarx source from all metrics."""
    # Added after Quality-time v5.49.0, see https://github.com/ICTU/quality-time/issues/12798
    change_description = ""
    for metric in metrics(report):
        sources = metric.get("sources", {})
        if source_ids_to_remove := [source_id for source_id, source in sources.items() if source["type"] == "cxsast"]:
            change_description = "remove the Checkmarx source from metrics"
            for source_id in source_ids_to_remove:
                del metric["sources"][source_id]
    return change_description


def remove_subject_description(report) -> str:
    """Remove the description field from all subjects."""
    # Added after Quality-time v5.50.0, see https://github.com/ICTU/quality-time/issues/12799
    change_description = ""
    for subject in report.get("subjects", {}).values():
        if "description" in subject:
            change_description = "remove the description field from subjects"
            del subject["description"]
    return change_description


def metrics(report):
    """Return the metrics in the report."""
    for subject in report.get("subjects", {}).values():
        yield from subject.get("metrics", {}).values()


def replace_document(collection: Collection, document) -> None:
    """Replace the document in the collection."""
    document_id = document["_id"]
    del document["_id"]
    collection.replace_one({"_id": document_id}, document)
