"""Measurement routes."""

import logging
import time
from collections.abc import Iterator
from datetime import timedelta
from typing import cast

import bottle
from pymongo.database import Database

from shared.database.measurements import insert_new_measurement, latest_measurement
from shared.model.measurement import Measurement
from shared.utils.date_time import now
from shared.utils.functions import first
from shared.utils.type import MetricId, SourceId

from database import sessions
from database.measurements import count_measurements, all_metric_measurements, measurements_in_period
from database.reports import latest_report_for_uuids, latest_reports
from utils.functions import report_date_time

from .plugins.auth_plugin import EDIT_ENTITY_PERMISSION


@bottle.post(
    "/api/v3/measurement/<metric_uuid>/source/<source_uuid>/entity/<entity_key>/<attribute>",
    permissions_required=[EDIT_ENTITY_PERMISSION],
)
def set_entity_attribute(
    metric_uuid: MetricId,
    source_uuid: SourceId,
    entity_key: str,
    attribute: str,
    database: Database,
) -> Measurement:
    """Set an entity attribute."""
    report = latest_report_for_uuids(latest_reports(database), metric_uuid)[0]
    metric = report.metrics_dict[metric_uuid]
    new_measurement = cast(Measurement, latest_measurement(database, metric)).copy()
    source = first(new_measurement["sources"], lambda source: source["source_uuid"] == source_uuid)
    entity = first(source["entities"], lambda entity: entity["key"] == entity_key)
    entity_description = "/".join([str(entity[key]) for key in entity if key not in ("key", "url")])
    old_value = source.get("entity_user_data", {}).get(entity_key, {}).get(attribute) or ""
    new_value = dict(bottle.request.json)[attribute]
    user = sessions.find_user(database)
    description = f"{user.name()} changed the {attribute} of '{entity_description}' from '{old_value}' to '{new_value}'"
    entity_user_data = source.setdefault("entity_user_data", {}).setdefault(entity_key, {})
    entity_user_data[attribute] = new_value
    if attribute == "status":
        desired_reponse_time = report.desired_measurement_entity_response_time(new_value)
        end_date = str((now() + timedelta(days=desired_reponse_time)).date()) if desired_reponse_time else None
        entity_user_data["status_end_date"] = end_date
        description += f" and changed the status end date to '{end_date}'"
    new_measurement["delta"] = {
        "uuids": [report.uuid, metric.subject_uuid, metric_uuid, source_uuid],
        "description": description + ".",
        "email": user.email,
    }
    return insert_new_measurement(database, new_measurement)


def sse_pack(event_id: int, event: str, data: int, retry: str = "20000") -> str:
    """Pack data in Server-Sent Events (SSE) format."""
    return f"retry: {retry}\nid: {event_id}\nevent: {event}\ndata: {data}\n\n"


@bottle.get("/api/v3/nr_measurements", authentication_required=False)
def stream_nr_measurements(database: Database) -> Iterator[str]:
    """Return the number of measurements as server sent events."""
    # Keep event IDs consistent
    event_id = int(bottle.request.get_header("Last-Event-Id", -1)) + 1

    # Set the response headers
    # https://serverfault.com/questions/801628/for-server-sent-events-sse-what-nginx-proxy-configuration-is-appropriate
    bottle.response.set_header("Connection", "keep-alive")
    bottle.response.set_header("Content-Type", "text/event-stream")
    bottle.response.set_header("Cache-Control", "no-cache")
    bottle.response.set_header("X-Accel-Buffering", "no")

    # Provide an initial data dump to each new client and set up our message payload with a retry value in case of
    # connection failure
    nr_measurements = count_measurements(database)
    logging.info("Initializing nr_measurements stream with %s measurements", nr_measurements)
    yield sse_pack(event_id, "init", nr_measurements)
    skipped = 0
    max_skipped = 5
    # Now give the client updates as they arrive
    while True:
        time.sleep(10)
        if (new_nr_measurements := count_measurements(database)) > nr_measurements or skipped > max_skipped:
            skipped = 0
            nr_measurements = new_nr_measurements
            event_id += 1
            logging.info("Updating nr_measurements stream with %s measurements", nr_measurements)
            yield sse_pack(event_id, "delta", nr_measurements)
        else:
            skipped += 1


@bottle.get("/api/v3/measurements", authentication_required=False)
def get_measurements(database: Database):
    """Return all measurements (without details) for all reports between the date and the minimum date."""
    date_time = report_date_time()
    min_date_time = report_date_time("min_report_date")
    measurements = measurements_in_period(database, min_iso_timestamp=min_date_time, max_iso_timestamp=date_time)
    return {"measurements": measurements}


@bottle.get("/api/v3/measurements/<metric_uuid>", authentication_required=False)
def get_metric_measurements(metric_uuid: MetricId, database: Database) -> dict:
    """Return the measurements for the metric."""
    metric_uuid = cast(MetricId, metric_uuid.split("&")[0])
    return {"measurements": all_metric_measurements(database, metric_uuid, max_iso_timestamp=report_date_time())}
