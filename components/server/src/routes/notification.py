"""notification routes"""

import bottle
from pymongo.database import Database

from database import sessions
from database.datamodels import latest_datamodel
from database.reports import insert_new_report, latest_reports
from model.data import ReportData
from server_utilities.functions import uuid
from server_utilities.type import ReportId, NotificationDestinationId


@bottle.post("/api/v3/report/<report_uuid>/notification_destination/new")
def post_new_notification_destination(report_uuid: ReportId,
                                      database: Database):
    """Create a new notification destination."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database)
    data = ReportData(data_model, reports, report_uuid)
    if "notification_destinations" not in data.report:
        data.report["notification_destinations"] = {}
    data.report["notification_destinations"][(notification_destination_uuid := uuid())] = \
        dict(teams_webhook="", name="new", url="")

    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[report_uuid, notification_destination_uuid],
        email=user["email"],
        description=f"{user['user']} created a new destination for notifications in report '{data.report_name}'.")
    result = insert_new_report(database, data.report)
    result["new_destination_uuid"] = notification_destination_uuid
    return result


@bottle.post("/api/v3/report/<report_uuid>"
             "/notification_destination/<notification_destination_uuid>"
             "/attribute/<notification_destination_attribute>")
def post_notification_destination_attribute(report_uuid: ReportId,
                                            notification_destination_uuid: NotificationDestinationId,
                                            notification_destination_attribute: str, database: Database):
    """Set a specified notification destination attribute."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database)
    data = ReportData(data_model, reports, report_uuid)
    notification_destination_name = data.report["notification_destinations"][notification_destination_uuid]["name"]
    value = dict(bottle.request.json)[notification_destination_attribute]
    old_value = data.report["notification_destinations"][notification_destination_uuid].get(
        notification_destination_attribute) or ""
    data.report["notification_destinations"][notification_destination_uuid][notification_destination_attribute] = value

    if old_value == value:
        return dict(ok=True)  # Nothing to do
    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[data.report_uuid, notification_destination_uuid],
        email=user["email"],
        description=f"{user['user']} changed the {notification_destination_attribute} of notification destination "
                    f"'{notification_destination_name}' in report '{data.report_name}' "
                    f"from '{old_value}' to '{value}'.")
    return insert_new_report(database, data.report)
