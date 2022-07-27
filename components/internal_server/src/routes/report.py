"""Report routes."""

import bottle
from pymongo.database import Database

from shared.database.measurements import recent_measurements

from database.reports import latest_reports


@bottle.get("/api/report")
def get_report(database: Database) -> dict[str, list]:
    """Return the quality reports, including summaries of recent measurements."""
    reports = latest_reports(database)
    summarized_reports = []

    for report in reports:
        measurements = recent_measurements(database, report.metrics_dict)
        summarized_reports.append(report.summarize(measurements))

    return dict(reports=summarized_reports)
