"""notification routes"""

from typing import Any, Dict, List, Optional, Tuple, Union, cast

import bottle
import requests
from pymongo.database import Database

from database import sessions
from database.datamodels import default_source_parameters, latest_datamodel
from database.reports import insert_new_report, latest_reports
from model.actions import copy_source, move_item
from model.data import ReportData
from model.queries import is_password_parameter
from model.transformations import change_source_parameter
from server_utilities.functions import uuid
from server_utilities.type import URL, EditScope, MetricId, ReportId, SourceId, SubjectId


@bottle.post("/api/v3/report/<report_uuid>/notification_destination/new")
def post_new_notification_destination(report_uuid: ReportId, database: Database):
    """Create a new notification destination."""
    data_model = latest_datamodel(database)
    reports = latest_reports(database)
    data = ReportData(data_model, reports, report_uuid)
    if "notification_destinations" not in data.report:
        data.report["notification_destinations"] = {}
    data.report["notification_destinations"][(notification_destination_uuid := uuid())] = dict(teams_webhook="", name="new", url="")

    user = sessions.user(database)
    data.report["delta"] = dict(
        uuids=[report_uuid, notification_destination_uuid], email=user["email"],
        description=f"{user['user']} created a new destination for notifications in report '{data.report_name}'.")
    result = insert_new_report(database, data.report)
    result["new_destination_uuid"] = notification_destination_uuid
    return result
