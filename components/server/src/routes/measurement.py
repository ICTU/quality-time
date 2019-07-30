"""Measurement routes."""

import time
from typing import Dict, Iterator

import bottle
from pymongo.database import Database

from database.measurements import count_measurements, latest_measurement, recent_measurements, insert_new_measurement
from utilities.functions import report_date_time


@bottle.post("/measurement/<metric_uuid>/source/<source_uuid>/entity/<entity_key>/<attribute>")
def set_entity_attribute(metric_uuid: str, source_uuid: str, entity_key: str, attribute: str,
                         database: Database) -> Dict:
    """Set a entity attribute."""
    measurement = latest_measurement(database, metric_uuid)
    source = [s for s in measurement["sources"] if s["source_uuid"] == source_uuid][0]
    value = dict(bottle.request.json)[attribute]
    source.setdefault("entity_user_data", {}).setdefault(entity_key, {})[attribute] = value
    return insert_new_measurement(database, measurement)


def sse_pack(event_id: int, event: str, data: int, retry: str = "2000") -> str:
    """Pack data in Server-Sent Events (SSE) format."""
    return f"retry: {retry}\nid: {event_id}\nevent: {event}\ndata: {data}\n\n"


@bottle.get("/nr_measurements/<report_uuid>")
def stream_nr_measurements(report_uuid: str, database: Database) -> Iterator[str]:
    """Return the number of measurements for the given report as server sent events."""
    # Keep event IDs consistent
    event_id = int(bottle.request.get_header("Last-Event-Id", -1)) + 1

    # Set the response headers
    bottle.response.set_header("Content-Type", "text/event-stream")

    # Provide an initial data dump to each new client and set up our
    # message payload with a retry value in case of connection failure
    data = count_measurements(database, report_uuid)
    yield sse_pack(event_id, "init", data)

    # Now give the client updates as they arrive
    while True:
        time.sleep(10)
        new_data = count_measurements(database, report_uuid)
        if new_data > data:
            data = new_data
            event_id += 1
            yield sse_pack(event_id, "delta", data)


@bottle.get("/measurements/<metric_uuid>")
def get_measurements(metric_uuid: str, database: Database) -> Dict:
    """Return the measurements for the metric."""
    metric_uuid = metric_uuid.split("&")[0]
    measurements = []
    for measurement in recent_measurements(database, metric_uuid, report_date_time()):
        measurement["_id"] = str(measurement["_id"])
        measurements.append(measurement)
    return dict(measurements=measurements)
