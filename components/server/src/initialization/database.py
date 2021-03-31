"""Database initialization."""

import logging
import os

import pymongo  # pylint: disable=wrong-import-order
from pymongo.database import Database

from initialization.secrets import initialize_secrets
from model.iterators import metrics, sources

from .datamodel import import_datamodel
from .report import import_example_reports, initialize_reports_overview


# For some reason the init_database() function gets reported as partially uncovered by the feature tests. Ignore.


def init_database() -> Database:  # pragma: no cover-behave
    """Initialize the database connection and contents."""
    database_url = os.environ.get("DATABASE_URL", "mongodb://root:root@localhost:27017")
    database = pymongo.MongoClient(database_url).quality_time_db
    logging.info("Connected to database: %s", database)
    nr_reports = database.reports.count_documents({})
    nr_measurements = database.measurements.count_documents({})
    logging.info("Database has %d report documents and %d measurement documents", nr_reports, nr_measurements)
    create_indexes(database)
    import_datamodel(database)
    initialize_secrets(database)
    initialize_reports_overview(database)
    if os.environ.get("LOAD_EXAMPLE_REPORTS", "True").lower() == "true":
        import_example_reports(database)
    add_last_flag_to_reports(database)
    rename_ready_user_story_points_metric(database)
    rename_teams_webhook_notification_destination(database)
    rename_axe_selenium_python_to_axe_core(database)
    return database


def create_indexes(database: Database) -> None:
    """Create any indexes."""
    database.datamodels.create_index("timestamp")
    database.reports.create_index("timestamp")
    database.measurements.create_index("start")


def add_last_flag_to_reports(database: Database) -> None:
    """Add last flag to all reports."""
    # Introduced when the most recent version of Quality-time was 2.5.2.
    report_ids = []
    for report_uuid in database.reports.distinct("report_uuid"):
        report = database.reports.find_one(
            filter={"report_uuid": report_uuid}, sort=[("timestamp", pymongo.DESCENDING)]
        )
        report_ids.append(report["_id"])
    database.reports.update_many({"_id": {"$in": report_ids}}, {"$set": {"last": True}})


def rename_ready_user_story_points_metric(database: Database) -> None:  # pragma: no cover-behave
    """Rename the ready_user_story_points metric to user_story_points."""
    # Introduced when the most recent version of Quality-time was 3.3.0.
    reports = list(database.reports.find({"last": True, "deleted": {"$exists": False}}))
    for report in reports:
        changed = False
        for metric in metrics(report):
            if metric["type"] == "ready_user_story_points":
                metric["type"] = "user_story_points"
                changed = True
                if not metric.get("name"):
                    metric["name"] = "Ready user story points"
        if changed:
            replace_report(database, report)


def rename_teams_webhook_notification_destination(database: Database) -> None:  # pragma: no cover-behave
    """Rename the teams_webhook of notification_destination to webhook."""
    # Introduced when the most recent version of Quality-time was 3.16.0.
    reports = list(database.reports.find({"last": True, "deleted": {"$exists": False}}))
    for report in reports:
        changed = False
        for notification_destination in report.get("notification_destinations", {}).values():
            if "teams_webhook" in notification_destination:
                notification_destination["webhook"] = notification_destination.pop("teams_webhook")
                changed = True
        if changed:
            replace_report(database, report)


def rename_axe_selenium_python_to_axe_core(database: Database) -> None:  # pragma: no cover-behave
    """Rename the axe-selenium-python source to Axe-core."""
    # Introduced when the most recent version of Quality-time was 3.19.1.
    reports = list(database.reports.find({"last": True, "deleted": {"$exists": False}}))
    for report in reports:
        changed = False
        for source in sources(report):
            if source["type"] == "axe_selenium_python":
                source["type"] = "axe_core"
                if not source.get("name"):
                    source["name"] = "axe-selenium-python"
                changed = True
        if changed:
            replace_report(database, report)


def replace_report(database: Database, report) -> None:
    """Replace the report in the database with the new version."""
    report_id = report["_id"]
    del report["_id"]
    database.reports.replace_one({"_id": report_id}, report)
