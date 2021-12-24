"""Reports routes."""

import bottle
from pymongo.database import Database

from database.datamodels import latest_datamodel
from database.reports import latest_reports, latest_reports_overview

from ..database import sessions
from ..database.measurements import recent_measurements
from ..database.reports import insert_new_reports_overview
from ..model.transformations import hide_credentials
from ..utils.functions import report_date_time, sanitize_html

from .plugins.auth_plugin import EDIT_REPORT_PERMISSION


@bottle.get("/api/v3/reports_overview", authentication_required=False)
def get_reports_overview(database: Database):
    """Return all the quality reports."""
    return latest_reports_overview(database, report_date_time())


@bottle.get("/api/v3/reports", authentication_required=False)
def get_reports(database: Database):  # pragma: no cover
    """Return all the quality reports.

    DEPRECATED use /api/v3/reports_overview and /api/v3/report instead.
    """
    date_time = report_date_time()
    data_model = latest_datamodel(database, date_time)
    overview = latest_reports_overview(database, date_time)
    overview["reports"] = []
    reports = latest_reports(database, data_model, date_time)
    metrics_dict = {}
    for report in reports:
        metrics_dict.update(report.metrics_dict)
    measurements = recent_measurements(database, metrics_dict, date_time)
    for report in reports:
        overview["reports"].append(report.summarize(measurements))
    hide_credentials(data_model, *overview["reports"])
    return overview


@bottle.post("/api/v3/reports_overview/attribute/<reports_attribute>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_reports_overview_attribute(reports_attribute: str, database: Database):
    """Set a reports overview attribute."""
    new_value = dict(bottle.request.json)[reports_attribute]
    if reports_attribute == "comment" and new_value:
        new_value = sanitize_html(new_value)
    overview = latest_reports_overview(database)
    old_value = overview.get(reports_attribute)
    if new_value == old_value:
        return dict(ok=True)  # Nothing to do

    user = sessions.user(database)

    if reports_attribute == "permissions" and EDIT_REPORT_PERMISSION in new_value:
        report_editors = new_value[EDIT_REPORT_PERMISSION]
        if len(report_editors) > 0 and user["user"] not in report_editors and user["email"] not in report_editors:
            new_value[EDIT_REPORT_PERMISSION].append(user["user"])

    overview[reports_attribute] = new_value
    value_change_description = "" if reports_attribute == "layout" else f" from '{old_value}' to '{new_value}'"
    delta_description = f"{{user}} changed the {reports_attribute} of the reports overview{value_change_description}."

    return insert_new_reports_overview(database, delta_description, overview)
