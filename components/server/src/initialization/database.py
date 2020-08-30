"""Database initialization."""

import logging
import os

import pymongo  # pylint: disable=wrong-import-order
from pymongo.database import Database

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
    initialize_reports_overview(database)
    if os.environ.get("LOAD_EXAMPLE_REPORTS", "True").lower() == "true":
        import_example_reports(database)
    add_last_flag_to_reports(database)
    rename_ready_user_story_points_metric(database)
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
            filter={"report_uuid": report_uuid}, sort=[("timestamp", pymongo.DESCENDING)])
        report_ids.append(report["_id"])
    database.reports.update_many({"_id": {"$in": report_ids}}, {"$set": {"last": True}})


def rename_ready_user_story_points_metric(database: Database) -> None:  # pragma: no cover-behave
    """Rename the ready_user_story_points metric to user_story_points."""
    # Introduced when the most recent version of Quality-time was 3.3.0.
    reports = list(database.reports.find({"last": True, "deleted": {"$exists": False}}))
    for report in reports:
        changed = False
        for subject in report["subjects"].values():
            for metric in subject["metrics"].values():
                if metric["type"] == "ready_user_story_points":
                    metric["type"] = "user_story_points"
                    changed = True
                    if not metric.get("name"):
                        metric["name"] = "Ready user story points"
        if changed:
            report_id = report["_id"]
            del report["_id"]
            database.reports.replace_one({"_id": report_id}, report)
