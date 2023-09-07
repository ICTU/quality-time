"""Reports collection."""

from pymongo.database import Database

from shared.database.filters import DOES_NOT_EXIST
from shared.model.report import Report
from shared_data_model import DATA_MODEL


def get_reports(database: Database, report_class: type[Report] = Report) -> list[Report]:
    """Return a list of reports."""
    query = {"last": True, "deleted": DOES_NOT_EXIST}
    return [report_class(DATA_MODEL.model_dump(), report_dict) for report_dict in database.reports.find(filter=query)]
