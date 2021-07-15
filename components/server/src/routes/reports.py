"""Reports routes."""

import bottle
from pymongo.database import Database

from database import sessions
from database.reports import insert_new_reports_overview, latest_reports_overview
from routes.plugins.auth_plugin import EDIT_REPORT_PERMISSION
from server_utilities.functions import report_date_time


@bottle.get("/api/v3/reports_overview", authentication_required=False)
def get_reports(database: Database):
    """Return all the quality reports."""
    date_time = report_date_time()
    overview = latest_reports_overview(database, date_time)
    return overview


@bottle.post("/api/v3/reports_overview/attribute/<reports_attribute>", permissions_required=[EDIT_REPORT_PERMISSION])
def post_reports_attribute(reports_attribute: str, database: Database):
    """Set a reports overview attribute."""
    value = dict(bottle.request.json)[reports_attribute]
    overview = latest_reports_overview(database)
    old_value = overview.get(reports_attribute)
    if value == old_value:
        return dict(ok=True)  # Nothing to do

    user = sessions.user(database)

    if reports_attribute == "permissions" and EDIT_REPORT_PERMISSION in value:
        report_editors = value[EDIT_REPORT_PERMISSION]
        if len(report_editors) > 0 and user["user"] not in report_editors and user["email"] not in report_editors:
            value[EDIT_REPORT_PERMISSION].append(user["user"])

    overview[reports_attribute] = value
    value_change_description = "" if reports_attribute == "layout" else f" from '{old_value}' to '{value}'"
    delta_description = f"{{user}} changed the {reports_attribute} of the reports overview{value_change_description}."

    return insert_new_reports_overview(database, delta_description, overview)
