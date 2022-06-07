"""Notification routes."""

import bottle
from pymongo.database import Database

from shared.database.datamodels import latest_datamodel
from shared.utils.type import ReportId

from database.reports import insert_new_report, latest_report
from utils.functions import uuid
from utils.type import NotificationDestinationId

from .plugins.auth_plugin import EDIT_REPORT_PERMISSION


@bottle.post("/api/v3/report/<report_uuid>/notification_destination/new", permissions_required=[EDIT_REPORT_PERMISSION])
def post_new_notification_destination(report_uuid: ReportId, database: Database):
    """Create a new notification destination."""
    data_model = latest_datamodel(database)
    report = latest_report(database, data_model, report_uuid)
    if "notification_destinations" not in report:
        report["notification_destinations"] = {}
    report["notification_destinations"][(notification_destination_uuid := uuid())] = dict(
        webhook="", name="Microsoft Teams webhook", sleep_duration=0
    )
    delta_description = f"{{user}} created a new destination for notifications in report '{report.name}'."
    uuids = [report_uuid, notification_destination_uuid]
    result = insert_new_report(database, delta_description, uuids, report)
    result["new_destination_uuid"] = notification_destination_uuid
    return result


@bottle.delete(
    "/api/v3/report/<report_uuid>/notification_destination/<notification_destination_uuid>",
    permissions_required=[EDIT_REPORT_PERMISSION],
)
def delete_notification_destination(
    report_uuid: ReportId, notification_destination_uuid: NotificationDestinationId, database: Database
):
    """Delete a destination from a report."""
    data_model = latest_datamodel(database)
    report = latest_report(database, data_model, report_uuid)
    destination_name = report["notification_destinations"][notification_destination_uuid]["name"]
    del report["notification_destinations"][notification_destination_uuid]
    delta_description = f"{{user}} deleted destination {destination_name} from report '{report.name}'."
    uuids = [report_uuid, notification_destination_uuid]
    return insert_new_report(database, delta_description, uuids, report)


@bottle.post(
    "/api/v3/report/<report_uuid>/notification_destination/<notification_destination_uuid>/attributes",
    permissions_required=[EDIT_REPORT_PERMISSION],
)
def post_notification_destination_attributes(
    report_uuid: ReportId, notification_destination_uuid: NotificationDestinationId, database: Database
):
    """Set specified notification destination attributes."""
    data_model = latest_datamodel(database)
    report = latest_report(database, data_model, report_uuid)
    notification_destination_name = report["notification_destinations"][notification_destination_uuid]["name"]
    attributes = dict(bottle.request.json)
    old_values = []
    for key in attributes:
        old_values.append(report["notification_destinations"][notification_destination_uuid].get(key) or "")
        report["notification_destinations"][notification_destination_uuid][key] = attributes[key]

    if set(old_values) == set(attributes.values()):
        return dict(ok=True)  # Nothing to do

    separator = "' and '"
    delta_description = (
        f"{{user}} changed the '{separator.join(attributes.keys())}' of notification destination "
        f"'{notification_destination_name}' in report '{report.name}' "
        f"from '{separator.join(old_values)}' to '{separator.join(attributes.values())}'."
    )
    uuids = [report_uuid, notification_destination_uuid]
    return insert_new_report(database, delta_description, uuids, report)
