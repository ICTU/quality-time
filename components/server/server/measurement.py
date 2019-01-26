"""Measurement API."""

import json
import logging
import time
from distutils.version import LooseVersion
from typing import Optional

import bottle
import pymongo

from .util import iso_timestamp, report_date_time


def determine_status(value: Optional[str], target: str, direction: str) -> Optional[str]:
    """Determine the status of the measurement from the value and target."""
    if value is None:
        status = None
    else:
        try:
            target = int(target)
            value = int(value)
        except ValueError:
            # Assume we deal with version numbers
            target = LooseVersion(str(target))
            value = LooseVersion(value)
        if direction == "<=":
            status = "target_met" if value <= target else "target_not_met"
        elif direction == ">=":
            status = "target_met" if value >= target else "target_not_met"
        else:
            status = "target_met" if value == target else "target_not_met"
    return status


@bottle.post("/measurement")
def post_measurement(database) -> None:
    """Put the measurement in the database."""
    def equal_measurements(measure1, measure2):
        """Return whether the measurements are equal."""
        return measure1["measurement"] == measure2["measurement"] and \
               measure1["calculation_error"] == measure2["calculation_error"]

    measurement = bottle.request.json
    timestamp_string = iso_timestamp()
    metric = database.metrics.find_one(filter={"metric": measurement["metric"]["metric"]})
    if not metric:
        logging.error("Can't find %s metric in Metrics collection.", measurement["metric"]["metric"])
        return
    latest_measurement_doc = database.measurements.find_one(
        filter={"metric": measurement["metric"]}, sort=[("measurement.start", pymongo.DESCENDING)])
    if latest_measurement_doc:
        if equal_measurements(latest_measurement_doc["measurement"], measurement["measurement"]):
            database.measurements.update_one(
                filter={"_id": latest_measurement_doc["_id"]},
                update={"$set": {"measurement.end": timestamp_string}})
            return
        comment = latest_measurement_doc["comment"]  # Reuse comment of previous measurement
        target = latest_measurement_doc["measurement"]["target"]  # Reuse target too
    else:
        comment = ""
        target = metric["default_target"]
    measurement["measurement"]["start"] = timestamp_string
    measurement["measurement"]["end"] = timestamp_string
    measurement["measurement"]["target"] = target
    measurement["comment"] = comment
    value = measurement["measurement"]["measurement"]
    measurement["measurement"]["status"] = determine_status(value, target, metric["direction"])
    database.measurements.insert_one(measurement)


def sse_pack(event_id: str, event: str, data: str, retry: str = "2000") -> str:
    """Pack data in Server-Sent Events (SSE) format"""
    return f"retry: {retry}\nid: {event_id}\nevent: {event}\ndata: {data}\n\n"


@bottle.get("/nr_measurements")
def stream_nr_measurements(database):
    """Return the number of measurements as server sent events."""
    # Keep event IDs consistent
    event_id = int(bottle.request.get_header("Last-Event-Id", -1)) + 1

    # Set the response headers
    bottle.response.set_header("Content-Type", "text/event-stream")

    # Provide an initial data dump to each new client and set up our
    # message payload with a retry value in case of connection failure
    data = database.measurements.count_documents({})
    yield sse_pack(event_id, "init", data)

    # Now give the client updates as they arrive
    while True:
        time.sleep(10)
        new_data = database.measurements.count_documents({})
        if new_data > data:
            data = new_data
            event_id += 1
            yield sse_pack(event_id, "delta", data)


@bottle.get("/measurements/<metric:path>")
def get_measurements(metric: str, database):
    """Return the measurements for the metric/source."""
    metric = json.loads(metric.split("&")[0])
    docs = database.measurements.find(
        filter={"metric": metric, "measurement.start": {"$lt": report_date_time()}})
    measurements = []
    for measurement in docs:
        measurement["_id"] = str(measurement["_id"])
        measurements.append(measurement)
    return dict(measurements=measurements)
