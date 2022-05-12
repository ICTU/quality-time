"""Report routes."""

import bottle
from pymongo.database import Database

from shared.database.datamodels import latest_datamodel
from shared.database.measurements import recent_measurements

from database.reports import latest_reports


@bottle.get("/api/v3/report", authentication_required=False)
def get_report(database: Database):
    """Return the quality report, including information about other reports needed for move/copy actions."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database, data_model)
    summarized_reports = []

    for report in reports:
        measurements = recent_measurements(database, report.metrics_dict)
        summarized_reports.append(report.summarize(measurements))

    return dict(reports=summarized_reports)
