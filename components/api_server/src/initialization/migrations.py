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
        if change_description := remove_metric_addition(report):
            logger.info("Updating report %s to %s", report_uuid, change_description)
            replace_document(database.reports, report)


def remove_metric_addition(report) -> str:
    """Remove the addition field from all metrics."""
    # Added after Quality-time v5.47.1, see https://github.com/ICTU/quality-time/issues/12142
    change_description = ""
    for subject in report["subjects"].values():
        for metric in subject["metrics"].values():
            if "addition" in metric:
                change_description = "remove the addition field from metrics"
                del metric["addition"]
    return change_description


def replace_document(collection: Collection, document) -> None:
    """Replace the document in the collection."""
    document_id = document["_id"]
    del document["_id"]
    collection.replace_one({"_id": document_id}, document)
