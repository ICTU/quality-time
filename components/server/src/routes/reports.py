"""Reports routes."""

import bottle
from pymongo.database import Database

from database import sessions
from database.datamodels import latest_datamodel
from database.measurements import recent_measurements_by_metric_uuid
from database.reports import insert_new_reports_overview, latest_reports, latest_reports_overview
from model.transformations import hide_credentials, summarize_report
from server_utilities.functions import report_date_time


@bottle.get("/api/v3/reports")
def get_reports(database: Database):
    """Return the quality reports."""
    date_time = report_date_time()
    data_model = latest_datamodel(database, date_time)
    overview = latest_reports_overview(database, date_time)
    overview["reports"] = []
    recent_measurements = recent_measurements_by_metric_uuid(database, date_time)
    for report in latest_reports(database, date_time):
        summarize_report(report, recent_measurements, data_model)
        overview["reports"].append(report)
    hide_credentials(data_model, *overview["reports"])
    return overview


@bottle.post("/api/v3/reports/attribute/<reports_attribute>")
def post_reports_attribute(reports_attribute: str, database: Database):
    """Set a reports overview attribute."""
    value = dict(bottle.request.json)[reports_attribute]
    overview = latest_reports_overview(database)
    old_value = overview.get(reports_attribute)
    if value == old_value:
        return dict(ok=True)  # Nothing to do
    user = sessions.user(database)
    if reports_attribute == "editors" and len(value) > 0 and user["user"] not in value and user["email"] not in value:
        value.append(user["user"])  # Make sure users don't remove themselves as editor by accident
    overview[reports_attribute] = value
    value_change_description = "" if reports_attribute == "layout" else f" from '{old_value}' to '{value}'"
    overview["delta"] = dict(
        email=user["email"],
        description=f"{user['user']} changed the {reports_attribute} of the reports overview"
        f"{value_change_description}.",
    )
    return insert_new_reports_overview(database, overview)
