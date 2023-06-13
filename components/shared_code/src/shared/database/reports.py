"""Module with collection of methods that touch multiple data types."""

from pymongo.database import Database

from shared.model.report import Report
from shared_data_model import DATA_MODEL


def get_reports(database: Database) -> list[Report]:
    """Return a list of reports."""
    query = {"last": True, "deleted": {"$exists": False}}
    return [Report(DATA_MODEL.dict(), report_dict) for report_dict in database["reports"].find(filter=query)]
