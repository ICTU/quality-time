"""Notification routes."""

import bottle
from pymongo.database import Database

from database.datamodels import latest_datamodel
from database.reports import insert_new_report, latest_reports
from model.data import ReportData
from server_utilities.functions import uuid
from server_utilities.type import ReportId, NotificationDestinationId


@bottle.post("/api/v3/report/<report_uuid>/notification_destination/new")
def post_new_notification_destination(report_uuid: ReportId, database: Database):
    """Create a new notification destination."""
    data = ReportData(latest_datamodel(database), latest_reports(database), report_uuid)
    if "notification_destinations" not in data.report:
        data.report["notification_destinations"] = {}
    data.report["notification_destinations"][(notification_destination_uuid := uuid())] = dict(
        teams_webhook="", name="Microsoft Teams webhook", sleep_duration=0
    )
    data.report["delta"] = dict(
        uuids=[report_uuid, notification_destination_uuid],
        description=f"{{user}} created a new destination for notifications in report '{data.report_name}'.",
    )
    result = insert_new_report(database, data.report)
    result["new_destination_uuid"] = notification_destination_uuid
    return result


@bottle.delete("/api/v3/report/<report_uuid>/notification_destination/<notification_destination_uuid>")
def delete_notification_destination(
    report_uuid: ReportId, notification_destination_uuid: NotificationDestinationId, database: Database
):
    """Delete a destination from a report."""
    data = ReportData(latest_datamodel(database), latest_reports(database), report_uuid)
    destination_name = data.report["notification_destinations"][notification_destination_uuid]["name"]
    del data.report["notification_destinations"][notification_destination_uuid]
    data.report["delta"] = dict(
        uuids=[report_uuid, notification_destination_uuid],
        description=f"{{user}} deleted destination {destination_name} from report '{data.report_name}'.",
    )
    return insert_new_report(database, data.report)


@bottle.post("/api/v3/report/<report_uuid>/notification_destination/<notification_destination_uuid>/attributes")
def post_notification_destination_attributes(
    report_uuid: ReportId, notification_destination_uuid: NotificationDestinationId, database: Database
):
    """Set specified notification destination attributes."""
    data = ReportData(latest_datamodel(database), latest_reports(database), report_uuid)
    notification_destination_name = data.report["notification_destinations"][notification_destination_uuid]["name"]
    attributes = dict(bottle.request.json)
    old_values = []
    for key in attributes:
        old_values.append(data.report["notification_destinations"][notification_destination_uuid].get(key) or "")
        data.report["notification_destinations"][notification_destination_uuid][key] = attributes[key]

    if set(old_values) == set(attributes.values()):
        return dict(ok=True)  # Nothing to do

    separator = "' and '"
    data.report["delta"] = dict(
        uuids=[data.report_uuid, notification_destination_uuid],
        description=f"{{user}} changed the '{separator.join(attributes.keys())}' of notification destination "
        f"'{notification_destination_name}' in report '{data.report_name}' "
        f"from '{separator.join(old_values)}' to '{separator.join(attributes.values())}'.",
    )
    return insert_new_report(database, data.report)
