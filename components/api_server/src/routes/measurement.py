"""Measurement routes."""

import time
from typing import cast, TYPE_CHECKING

import bottle

from shared.database.measurements import insert_new_measurement, latest_measurement
from shared.model.measurement import Measurement
from shared.utils.functions import first
from shared.utils.type import MetricId, SourceId

from database import sessions
from database.measurements import count_measurements, all_metric_measurements, measurements_in_period
from database.reports import latest_report_for_uuids, latest_reports
from utils.functions import report_date_time
from utils.log import get_logger

from .plugins.auth_plugin import EDIT_ENTITY_PERMISSION

if TYPE_CHECKING:
    from collections.abc import Iterator

    from pymongo.database import Database


@bottle.post(
    "/api/internal/measurement/<metric_uuid>/source/<source_uuid>/entity/<entity_key>/<attribute>",
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
        new_end_date = report.deadline(new_value)
        old_end_date = entity_user_data.get("status_end_date")
        if new_end_date != old_end_date:
            entity_user_data["status_end_date"] = new_end_date
            description += f" and changed the status end date from '{old_end_date}' to '{new_end_date}'"
    new_measurement["delta"] = {
        "uuids": [report.uuid, metric.subject_uuid, metric_uuid, source_uuid],
        "description": description + ".",
        "email": user.email,
    }
    return insert_new_measurement(database, new_measurement)


def sse_pack(event_id: int, event: str, data: str, retry: str = "2000") -> str:
    """Pack data in Server-Sent Events (SSE) format."""
    return f"retry: {retry}\nid: {event_id}\nevent: {event}\ndata: {data}\n\n"


@bottle.get("/api/internal/nr_measurements", authentication_required=False)
def stream_nr_measurements(database: Database) -> Iterator[str]:
    """Return the number of measurements as server sent events."""
    logger = get_logger()
    # Keep event IDs consistent
    event_id = int(bottle.request.get_header("Last-Event-Id", -1)) + 1

    # Set the response headers
    # https://serverfault.com/questions/801628/for-server-sent-events-sse-what-nginx-proxy-configuration-is-appropriate
    bottle.response.set_header("Connection", "keep-alive")
    bottle.response.set_header("Content-Type", "text/event-stream")
    bottle.response.set_header("Cache-Control", "no-cache")
    bottle.response.set_header("X-Accel-Buffering", "no")

    # Provide the current number of measurements and a retry value to use in case of connection failure
    nr_measurements = count_measurements(database)
    logger.info("Initializing nr_measurements stream with %d measurements (event id = %d)", nr_measurements, event_id)
    yield sse_pack(event_id, "init", str(nr_measurements))
    event_id += 1

    # Flush the buffer that prevents messages from being sent immediately by sending a large message
    # Who or what is causing the buffering (bottle?, gevent?, nginx?), is a mystery, unfortunately
    yield sse_pack(event_id, "flush", "." * 256**2)

    # Now send the client the number of measurements periodically
    while True:
        time.sleep(10)
        nr_measurements = count_measurements(database)
        event_id += 1
        logger.info("Updating nr_measurements stream with %d measurements (event id = %d)", nr_measurements, event_id)
        yield sse_pack(event_id, "delta", str(nr_measurements))


@bottle.get("/api/internal/measurements", authentication_required=False)
def get_measurements(database: Database):
    """Return all measurements (without details) for all reports between the date and the minimum date."""
    date_time = report_date_time()
    min_date_time = report_date_time("min_report_date")
    measurements = measurements_in_period(database, min_iso_timestamp=min_date_time, max_iso_timestamp=date_time)
    return {"measurements": measurements}


@bottle.get("/api/internal/measurements/<metric_uuid>", authentication_required=False)
def get_metric_measurements(metric_uuid: MetricId, database: Database) -> dict:
    """Return the measurements for the metric."""
    metric_uuid = cast(MetricId, metric_uuid.split("&")[0])
    return {"measurements": all_metric_measurements(database, metric_uuid, max_iso_timestamp=report_date_time())}
