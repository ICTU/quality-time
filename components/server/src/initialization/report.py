"""Report loaders."""

import json
import logging
import pathlib

from pymongo.database import Database

from database.reports import insert_new_report, insert_new_reports_overview, latest_reports_overview, report_exists


def initialize_reports_overview(database: Database) -> None:
    """Initialize the reports overview if not present in the database."""
    # The coverage measurement of the behave feature tests is unstable. Most of the time it reports the last two lines
    # as covered, sometimes not. It's unclear why. To prevent needless checking of the coverage report coverage
    # measurement of the last two lines and the if-statement has been turned off.
    if latest_reports_overview(database):  # pragma: no cover-behave
        logging.info("Skipping initializing reports overview; it already exists")
    else:
        logging.info("Initializing reports overview")  # pragma: no cover-behave
        insert_new_reports_overview(
            database, "{{user}} initialized the reports overview", dict(title="Reports", subtitle="")
        )  # pragma: no cover-behave


def import_report(database: Database, filename: pathlib.Path) -> None:
    """Read the report and store it in the database."""
    # The coverage measurement of the behave feature tests is unstable. Most of the time it reports the last two lines
    # as covered, sometimes not. It's unclear why. To prevent needless checking of the coverage report coverage
    # measurement of the last two lines and the if-statement has been turned off.
    with filename.open() as json_report:
        imported_report = json.load(json_report)
    if report_exists(database, imported_report["report_uuid"]):  # pragma: no cover-behave
        logging.info("Skipping import of %s; it already exists", filename)
    else:  # pragma: no cover-behave
        insert_new_report(database, "{{user}} imported a new report", (imported_report, imported_report["report_uuid"]))
        logging.info("Report %s imported", filename)


def import_example_reports(database: Database) -> None:
    """Import the example reports."""
    example_reports_path = pathlib.Path(__file__).resolve().parent.parent / "example-reports"
    for filename in example_reports_path.glob("example-report*.json"):
        import_report(database, filename)
