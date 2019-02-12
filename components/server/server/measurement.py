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
        if isinstance(source["data"], list):
            value += len([unit for unit in source["data"] if unit["key"] not in source.get("hidden_units", [])])
        else:
            value += int(source["data"])
    return str(value)


@bottle.post("/measurements")
def post_measurement(database) -> None:
    """Put the measurement in the database."""
    measurement = dict(bottle.request.json)
    timestamp_string = iso_timestamp()
    latest_measurement = database.measurements.find_one(
        filter={"metric_uuid": measurement["metric_uuid"]}, sort=[("start", pymongo.DESCENDING)])
    if latest_measurement:
        # Copy the list of hidden source data keys to the new measurement and remove the hidden data
        for source, latest_source in zip(measurement["sources"], latest_measurement["sources"]):
            if "hidden_data" in latest_source:
                source["hidden_data"] = latest_source["hidden_data"]
                for item in source["data"][:]:
                    if item["key"] in source["hidden_data"]:
                        source["data"].remove(item)
        # If the new measurement is equal to the previous one, merge them together
        if latest_measurement["sources"] == measurement["sources"]:
            database.measurements.update_one(
                filter={"_id": latest_measurement["_id"]}, update={"$set": {"end": timestamp_string}})
            return
    measurement["value"] = calculate_measurement_value(measurement["sources"])
    measurement["start"] = measurement["end"] = timestamp_string
    database.measurements.insert_one(measurement)


@bottle.post("/measurements/<metric_uuid>/source/<source_uuid>/unit/<unit_key>/hide")
def hide_source_unit(metric_uuid: str, source_uuid: str, unit_key: str, database):
    """Hide the source unit."""
    timestamp_string = iso_timestamp()
    measurement = database.measurements.find_one(
        filter={"metric_uuid": metric_uuid}, sort=[("start", pymongo.DESCENDING)])
    del measurement["_id"]
    measurement["start"] = measurement["end"] = timestamp_string
    for source in measurement["sources"]:
        if source["source_uuid"] == source_uuid:
            if "hidden_data" not in source:
                source["hidden_data"] = []
            if unit_key not in source["hidden_data"]:
                source["hidden_data"].append(unit_key)
            for item in source["data"][:]:
                if item["key"] == unit_key:
                    source["data"].remove(item)
            break
    measurement["value"] = calculate_measurement_value(measurement["sources"])
    database.measurements.insert_one(measurement)


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
