"""Database initialization."""

import logging
import os

import pymongo  # pylint: disable=wrong-import-order
from pymongo.database import Database

from .datamodel import import_datamodel
from .report import import_example_reports, initialize_reports_overview


def init_database() -> Database:
    """Initialize the database connection and contents."""
    database_url = os.environ.get("DATABASE_URL", "mongodb://root:root@localhost:27017")
    database = pymongo.MongoClient(database_url).quality_time_db
    logging.info("Connected to database: %s", database)
    create_indexes(database)
    nr_reports = database.reports.count_documents({})
    nr_measurements = database.measurements.count_documents({})
    logging.info("Database has %d report documents and %d measurement documents", nr_reports, nr_measurements)
    import_datamodel(database)
    initialize_reports_overview(database)
    if os.environ.get("LOAD_EXAMPLE_REPORTS", "True").lower() == "true":
        import_example_reports(database)
    update_database(database)
    return database


def create_indexes(database: Database) -> None:
    """Create any indexes."""
    database.reports.create_index("timestamp")


def update_database(database: Database) -> None:
    """Run any update statements. The version numbers below are the versions that were the latest version at the time
    the update statements were added."""

    # Remove the last flag on measurements [v1.7.0]
    database.measurements.update_many(filter={"last": True}, update={"$unset": {"last": ""}})

    # Remove summary, summary_by_subject, and summary_by_tag written to the reports collection by accident [v1.8.1]
    # See https://github.com/ICTU/quality-time/issues/1082.
    if count := database.reports.count_documents({"summary": {"$exists": True}}):
        logging.info("Removing unused fields from %d reports...", count)
        reports = database.reports.find({"summary": {"$exists": True}})
        for index, report in enumerate(reports):
            unset = {"summary": "", "summary_by_subject": "", "summary_by_tag": ""}
            for subject_uuid, subject in report.get("subjects", {}).items():
                for metric_uuid in subject.get("metrics", {}).keys():
                    for field in ["recent_measurements", "status", "value"]:
                        unset[f"subjects.{subject_uuid}.metrics.{metric_uuid}.{field}"] = ""
            logging.info(
                "Updating report %s (%d/%d): removing %d fields.", report["_id"], index + 1, count, len(unset))
            database.reports.update_one({"_id": report["_id"]}, update={"$unset": unset})
