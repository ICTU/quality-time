"""Measurement API."""

import time
from typing import Optional

import bottle
import pymongo

from .util import iso_timestamp, report_date_time


def calculate_measurement_value(sources) -> Optional[str]:
    """Calculate the measurement value from the source measurements."""
    value = 0
    for source in sources:
        if source["parse_error"] or source["connection_error"]:
            return None
        value += (int(source["value"]) - len(source.get("ignored_units", [])))
    return str(value)


def latest_measurement(metric_uuid: str, database):
    """Return the latest measurement."""
    return database.measurements.find_one(filter={"metric_uuid": metric_uuid}, sort=[("start", pymongo.DESCENDING)])


def insert_new_measurement(measurement, database):
    """Insert a new measurement."""
    measurement["value"] = calculate_measurement_value(measurement["sources"])
    measurement["start"] = measurement["end"] = iso_timestamp()
    database.measurements.insert_one(measurement)


@bottle.post("/measurements")
def post_measurement(database) -> None:
    """Put the measurement in the database."""
    measurement = dict(bottle.request.json)
    latest = latest_measurement(measurement["metric_uuid"], database)
    if latest:
        for latest_source, new_source in zip(latest["sources"], measurement["sources"]):
            if "ignored_units" in latest_source:
                # Copy the keys of ignored units that still exist in the new measurement
                new_unit_keys = set(unit["key"] for unit in new_source.get("units", []))
                new_source["ignored_units"] = [key for key in latest_source["ignored_units"] if key in new_unit_keys]
        if latest["sources"] == measurement["sources"]:
            # If the new measurement is equal to the previous one, merge them together
            database.measurements.update_one(filter={"_id": latest["_id"]}, update={"$set": {"end": iso_timestamp()}})
            return
    insert_new_measurement(measurement, database)


@bottle.post("/measurement/<metric_uuid>/source/<source_uuid>/unit/<unit_key>/ignore")
def ignore_source_unit(metric_uuid: str, source_uuid: str, unit_key: str, database):
    """Ignore or stop ignoring the source unit."""
    measurement = latest_measurement(metric_uuid, database)
    del measurement["_id"]
    source = [s for s in measurement["sources"] if s["source_uuid"] == source_uuid][0]
    if "ignored_units" not in source:
        source["ignored_units"] = []
    if unit_key in source["ignored_units"]:
        source["ignored_units"].remove(unit_key)
    else:
        source["ignored_units"].append(unit_key)
    insert_new_measurement(measurement, database)


def sse_pack(event_id: str, event: str, data: str, retry: str = "2000") -> str:
    """Pack data in Server-Sent Events (SSE) format"""
    return f"retry: {retry}\nid: {event_id}\nevent: {event}\ndata: {data}\n\n"


@bottle.get("/nr_measurements/<report_uuid>")
def stream_nr_measurements(report_uuid: str, database):
    """Return the number of measurements for the given report as server sent events."""
    # Keep event IDs consistent
    event_id = int(bottle.request.get_header("Last-Event-Id", -1)) + 1

    # Set the response headers
    bottle.response.set_header("Content-Type", "text/event-stream")

    # Provide an initial data dump to each new client and set up our
    # message payload with a retry value in case of connection failure
    data = database.measurements.count_documents(filter={"report_uuid": report_uuid})
    yield sse_pack(event_id, "init", data)

    # Now give the client updates as they arrive
    while True:
        time.sleep(10)
        new_data = database.measurements.count_documents(filter={"report_uuid": report_uuid})
        if new_data > data:
            data = new_data
            event_id += 1
            yield sse_pack(event_id, "delta", data)


@bottle.get("/measurements/<metric_uuid>")
def get_measurements(metric_uuid: str, database):
    """Return the measurements for the metric."""
    metric_uuid = metric_uuid.split("&")[0]
    docs = database.measurements.find(
        filter={"metric_uuid": metric_uuid, "start": {"$lt": report_date_time()}})
    measurements = []
    for measurement in docs:
        measurement["_id"] = str(measurement["_id"])
        measurements.append(measurement)
    return dict(measurements=measurements)
