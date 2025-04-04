"""Notification routes."""

import bottle
from pymongo.database import Database

from shared.utils.type import ItemId, ReportId, NotificationDestinationId

from database.reports import insert_new_report
from model.report import Report
from utils.functions import uuid

from .plugins.auth_plugin import EDIT_REPORT_PERMISSION
from .report import with_report


@bottle.post(
    "/api/internal/report/<report_uuid>/notification_destination/new", permissions_required=[EDIT_REPORT_PERMISSION]
)
@with_report
def post_new_notification_destination(database: Database, report: Report, report_uuid: ReportId):
    """Create a new notification destination."""
    if "notification_destinations" not in report:
        report["notification_destinations"] = {}
    report["notification_destinations"][(notification_destination_uuid := uuid())] = {
        "webhook": "",
        "name": "Microsoft Teams webhook",
        "sleep_duration": 0,
        "report_url": dict(bottle.request.json)["report_url"],
    }
    delta_description = f"{{user}} created a new destination for notifications in report '{report.name}'."
    uuids = [report_uuid, notification_destination_uuid]
    result = insert_new_report(database, delta_description, uuids, report)
    result["new_destination_uuid"] = notification_destination_uuid
    return result


@bottle.delete(
    "/api/internal/report/<report_uuid>/notification_destination/<notification_destination_uuid>",
    permissions_required=[EDIT_REPORT_PERMISSION],
)
@with_report
def delete_notification_destination(
    database: Database,
    report: Report,
    report_uuid: ReportId,
    notification_destination_uuid: NotificationDestinationId,
):
    """Delete a destination from a report."""
    destination_name = report["notification_destinations"][notification_destination_uuid]["name"]
    del report["notification_destinations"][notification_destination_uuid]
    delta_description = f"{{user}} deleted destination {destination_name} from report '{report.name}'."
    uuids: list[ItemId] = [report_uuid, notification_destination_uuid]
    return insert_new_report(database, delta_description, uuids, report)


@bottle.post(
    "/api/internal/report/<report_uuid>/notification_destination/<notification_destination_uuid>/attributes",
    permissions_required=[EDIT_REPORT_PERMISSION],
)
@with_report
def post_notification_destination_attributes(
    database: Database,
    report: Report,
    report_uuid: ReportId,
    notification_destination_uuid: NotificationDestinationId,
):
    """Set specified notification destination attributes."""
    notification_destination = report["notification_destinations"][notification_destination_uuid]
    notification_destination_name = notification_destination["name"]
    attributes = dict(bottle.request.json)
    old_values = []
    for key, value in attributes.items():
        old_values.append(notification_destination.get(key) or "")
        notification_destination[key] = value

    if set(old_values) == set(attributes.values()):
        return {"ok": True}  # Nothing to do

    separator = "' and '"
    delta_description = (
        f"{{user}} changed the '{separator.join(attributes.keys())}' of notification destination "
        f"'{notification_destination_name}' in report '{report.name}' "
        f"from '{separator.join(old_values)}' to '{separator.join(attributes.values())}'."
    )
    uuids = [report_uuid, notification_destination_uuid]
    return insert_new_report(database, delta_description, uuids, report)
