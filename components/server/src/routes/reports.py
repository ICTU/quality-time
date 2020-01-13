"""Reports routes."""

import bottle
from pymongo.database import Database

from database import sessions
from database.reports import latest_datamodel, latest_summarized_reports, latest_reports_overview, \
    insert_new_reports_overview
from model.transformations import hide_credentials
from server_utilities.functions import report_date_time


@bottle.get("/api/v1/reports")
@bottle.get("/api/v2/reports")
def get_reports(database: Database):
    """Return the quality reports."""
    date_time = report_date_time()
    overview = latest_reports_overview(database, date_time)
    overview["reports"] = latest_summarized_reports(database, date_time)
    hide_credentials(latest_datamodel(database), *overview["reports"])
    return overview


@bottle.post("/api/v1/reports/<reports_attribute>")
@bottle.post("/api/v2/reports/attribute/<reports_attribute>")
def post_reports_attribute(reports_attribute: str, database: Database):
    """Set a reports overview attribute."""
    value = dict(bottle.request.json)[reports_attribute]
    overview = latest_reports_overview(database)
    old_value = overview.get(reports_attribute)
    overview[reports_attribute] = value
    value_change_description = "" if reports_attribute == "layout" else f" from '{old_value}' to '{value}'"
    overview["delta"] = dict(
        description=f"{sessions.user(database)} changed the {reports_attribute} of the reports overview"
                    f"{value_change_description}.")
    return insert_new_reports_overview(database, overview)
