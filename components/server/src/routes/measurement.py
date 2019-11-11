"""Measurement routes."""

import logging
import time
from typing import cast, Dict, Iterator

from pymongo.database import Database
import bottle

from database.measurements import count_measurements, latest_measurement, recent_measurements, insert_new_measurement, \
    update_measurement_end
from database.reports import latest_metric
from database import sessions
from server_utilities.functions import report_date_time
from server_utilities.type import MetricId, ReportId, SourceId


@bottle.post("/api/v1/measurements")
def post_measurement(database: Database) -> Dict:
    """Put the measurement in the database."""
    measurement = dict(bottle.request.json)
    if latest := latest_measurement(database, measurement["metric_uuid"]):
        for latest_source, new_source in zip(latest["sources"], measurement["sources"]):
            new_entity_keys = set(entity["key"] for entity in new_source.get("entities", []))
            # Copy the user data of entities that still exist in the new measurement
            for entity_key, attributes in latest_source.get("entity_user_data", {}).items():
                if entity_key in new_entity_keys:
                    new_source.setdefault("entity_user_data", {})[entity_key] = attributes
        if latest["sources"] == measurement["sources"]:
            # If the new measurement is equal to the previous one, merge them together
            update_measurement_end(database, latest["_id"])
            return dict(ok=True)
    metric = latest_metric(database, measurement["report_uuid"], measurement["metric_uuid"])
    return insert_new_measurement(database, metric, measurement)


@bottle.post("/api/v1/measurement/<metric_uuid>/source/<source_uuid>/entity/<entity_key>/<attribute>")
def set_entity_attribute(metric_uuid: MetricId, source_uuid: SourceId, entity_key: str, attribute: str,
                         database: Database) -> Dict:
    """Set a entity attribute."""
    measurement = latest_measurement(database, metric_uuid)
    source = [s for s in measurement["sources"] if s["source_uuid"] == source_uuid][0]
    entity = [e for e in source["entities"] if e["key"] == entity_key][0]
    entity_description = "/".join([entity[key] for key in entity.keys() if key not in ("key", "url")])
    old_value = source.get("entity_user_data", {}).get(entity_key, {}).get(attribute) or ""
    value = dict(bottle.request.json)[attribute]
    source.setdefault("entity_user_data", {}).setdefault(entity_key, {})[attribute] = value
    measurement["delta"] = \
        f"{sessions.user(database)} changed the {attribute} of '{entity_description}' from '{old_value}' to '{value}'."
    metric = latest_metric(database, measurement["report_uuid"], metric_uuid)
    return insert_new_measurement(database, metric, measurement)


def sse_pack(event_id: int, event: str, data: int, retry: str = "2000") -> str:
    """Pack data in Server-Sent Events (SSE) format."""
    return f"retry: {retry}\nid: {event_id}\nevent: {event}\ndata: {data}\n\n"


@bottle.get("/api/v1/nr_measurements/<report_uuid>")
def stream_nr_measurements(report_uuid: ReportId, database: Database) -> Iterator[str]:
    """Return the number of measurements for the given report as server sent events."""
    # Keep event IDs consistent
    event_id = int(bottle.request.get_header("Last-Event-Id", -1)) + 1

    # Set the response headers
    bottle.response.set_header("Content-Type", "text/event-stream")
    # See https://github.com/facebook/create-react-app/issues/1633 why the next header is needed when running locally
    # with the webpack proxy.
    bottle.response.set_header("Cache-Control", "no-transform")

    # Provide an initial data dump to each new client and set up our
    # message payload with a retry value in case of connection failure
    data = count_measurements(database, report_uuid)
    logging.info("Initializing nr_measurements stream for report %s with %s measurements", report_uuid, data)
    yield sse_pack(event_id, "init", data)

    # Now give the client updates as they arrive
    while True:
        time.sleep(10)
        if (new_data := count_measurements(database, report_uuid)) > data:
            data = new_data
            event_id += 1
            logging.info("Updating nr_measurements stream for report %s with %s measurements", report_uuid, data)
            yield sse_pack(event_id, "delta", data)
        else:
            yield ": keep-alive\n\n"


@bottle.get("/api/v1/measurements/<metric_uuid>")
def get_measurements(metric_uuid: MetricId, database: Database) -> Dict:
    """Return the measurements for the metric."""
    metric_uuid = cast(MetricId, metric_uuid.split("&")[0])
    measurements = []
    for measurement in recent_measurements(database, metric_uuid, report_date_time()):
        measurement["_id"] = str(measurement["_id"])
        measurements.append(measurement)
    return dict(measurements=measurements)
