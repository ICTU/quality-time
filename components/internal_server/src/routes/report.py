"""Report routes."""

import bottle
from pymongo.database import Database

from database.reports import latest_reports


@bottle.get("/api/report")
def get_reports(database: Database) -> dict[str, list]:
    """Return the quality reports."""
    # DeepSource somehow confuses latest_reports() with another latest_reports() that needs two arguments, suppress.
    reports = latest_reports(database)
    return dict(reports=reports)
