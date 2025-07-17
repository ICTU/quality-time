"""Report loaders."""

import json
import pathlib
from typing import TYPE_CHECKING

from database.reports import insert_new_report, insert_new_reports_overview, latest_reports_overview, report_exists
from utils.log import get_logger

if TYPE_CHECKING:
    from pymongo.database import Database


def initialize_reports_overview(database: Database) -> None:
    """Initialize the reports overview if not present in the database."""
    logger = get_logger()
    # The coverage measurement of the behave feature tests is unstable. Most of the time it reports the last two lines
    # as covered, sometimes not. It's unclear why. To prevent needless checking of the coverage report coverage
    # measurement of the last two lines and the if-statement has been turned off.
    if latest_reports_overview(database):  # pragma: no feature-test-cover
        logger.info("Skipping initializing reports overview; it already exists")
    else:
        logger.info("Initializing reports overview")  # pragma: no feature-test-cover
        insert_new_reports_overview(
            database,
            "{{user}} initialized the reports overview",
            {"title": "Reports", "subtitle": ""},
        )  # pragma: no feature-test-cover


def import_report(database: Database, filename: pathlib.Path) -> None:
    """Read the report and store it in the database."""
    logger = get_logger()
    # The coverage measurement of the behave feature tests is unstable. Most of the time it reports the last two lines
    # as covered, sometimes not. It's unclear why. To prevent needless checking of the coverage report coverage
    # measurement of the last two lines and the if-statement has been turned off.
    with filename.open() as json_report:
        imported_report = json.load(json_report)
    if report_exists(database, imported_report["report_uuid"]):  # pragma: no feature-test-cover
        logger.info("Skipping import of %s; it already exists", filename)
    else:  # pragma: no feature-test-cover
        insert_new_report(database, "{{user}} imported a new report", [imported_report["report_uuid"]], imported_report)
        logger.info("Report %s imported", filename)


def import_example_reports(database: Database) -> None:
    """Import the example reports."""
    example_reports_path = pathlib.Path(__file__).resolve().parent.parent / "example-reports"
    for filename in example_reports_path.glob("example-report*.json"):
        import_report(database, filename)
