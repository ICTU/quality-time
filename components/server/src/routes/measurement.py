"""Measurement routes."""

import logging
import time
from collections.abc import Iterator
from typing import cast

import bottle
from pymongo.database import Database

from database import sessions
from database.datamodels import latest_datamodel
from database.measurements import (
    measurements_by_metric,
    count_measurements,
    insert_new_measurement,
    latest_measurement,
    latest_successful_measurement,
    update_measurement_end,
)
from database.reports import latest_metric, latest_reports
from model.data import SourceData

from model.measurement import Measurement
from model.metric import Metric
from routes.plugins.auth_plugin import EDIT_ENTITY_PERMISSION
from server_utilities.functions import report_date_time
from server_utilities.type import MetricId, SourceId


def log_times(message, metric_uuid, times):  # pragma: no cover
    """Log the post measurement endpoint duration."""
    duration = times[-1] - times[0]
    if duration > 5:
        deltas = []
        for index, timestamp in list(enumerate(times))[1:]:
            deltas.append(round(timestamp - times[index - 1], 2))
        logging.info("%s for %s took %ss: %s", message, metric_uuid, round(duration, 1), deltas)


@bottle.post("/internal-api/v3/measurements", authentication_required=False)
def post_measurement(database: Database) -> None:
    """Put the measurement in the database."""
    times = [time.time()]
    measurement_data = dict(bottle.request.json)
    times.append(time.time())
    metric_uuid = measurement_data["metric_uuid"]
    times.append(time.time())
    if (metric := latest_metric(database, metric_uuid)) is None:
        return  # Metric does not exist, must've been deleted while being measured
    times.append(time.time())
    latest = latest_measurement(database, metric)
    times.append(time.time())
    measurement = Measurement(metric, measurement_data, previous_measurement=latest)
    times.append(time.time())
    if latest:
        latest_successful = latest_successful_measurement(database, metric)
        times.append(time.time())
        measurement.copy_entity_user_data(latest if latest_successful is None else latest_successful)
        times.append(time.time())
        if not latest.debt_target_expired() and latest.sources() == measurement.sources():
            # If the new measurement is equal to the previous one, merge them together
            update_measurement_end(database, latest["_id"])
            times.append(time.time())
            log_times("Updating latest measurement", metric_uuid, times)
            return
    insert_new_measurement(database, measurement)
    times.append(time.time())
    log_times("Inserting new measurement", metric_uuid, times)


@bottle.post(
    "/api/v3/measurement/<metric_uuid>/source/<source_uuid>/entity/<entity_key>/<attribute>",
    permissions_required=[EDIT_ENTITY_PERMISSION],
)
def set_entity_attribute(
    metric_uuid: MetricId, source_uuid: SourceId, entity_key: str, attribute: str, database: Database
) -> dict:
    """Set an entity attribute."""
    data = SourceData(latest_datamodel(database), latest_reports(database), source_uuid)
    metric = Metric(data.datamodel, data.metric, metric_uuid)
    old_measurement = cast(Measurement, latest_measurement(database, metric))
    new_measurement = old_measurement.copy()
    source = [s for s in new_measurement["sources"] if s["source_uuid"] == source_uuid][0]
    entity = [e for e in source["entities"] if e["key"] == entity_key][0]
    entity_description = "/".join([str(entity[key]) for key in entity.keys() if key not in ("key", "url")])
    old_value = source.get("entity_user_data", {}).get(entity_key, {}).get(attribute) or ""
    new_value = dict(bottle.request.json)[attribute]
    source.setdefault("entity_user_data", {}).setdefault(entity_key, {})[attribute] = new_value
    user = sessions.user(database)
    new_measurement["delta"] = dict(
        uuids=[data.report_uuid, data.subject_uuid, metric_uuid, source_uuid],
        description=f"{user['user']} changed the {attribute} of '{entity_description}' from '{old_value}' to "
        f"'{new_value}'.",
        email=user["email"],
    )
    return insert_new_measurement(database, new_measurement)


def sse_pack(event_id: int, event: str, data: int, retry: str = "2000") -> str:
    """Pack data in Server-Sent Events (SSE) format."""
    return f"retry: {retry}\nid: {event_id}\nevent: {event}\ndata: {data}\n\n"


@bottle.get("/api/v3/nr_measurements", authentication_required=False)
def stream_nr_measurements(database: Database) -> Iterator[str]:
    """Return the number of measurements as server sent events."""
    # Keep event IDs consistent
    event_id = int(bottle.request.get_header("Last-Event-Id", -1)) + 1

    # Set the response headers
    bottle.response.set_header("Connection", "keep-alive")
    bottle.response.set_header("Content-Type", "text/event-stream")
    bottle.response.set_header("Cache-Control", "no-cache")

    # Provide an initial data dump to each new client and set up our message payload with a retry value in case of
    # connection failure
    nr_measurements = count_measurements(database)
    logging.info("Initializing nr_measurements stream with %s measurements", nr_measurements)
    yield sse_pack(event_id, "init", nr_measurements)
    skipped = 0
    # Now give the client updates as they arrive
    while True:
        time.sleep(10)
        if (new_nr_measurements := count_measurements(database)) > nr_measurements or skipped > 5:
            skipped = 0
            nr_measurements = new_nr_measurements
            event_id += 1
            logging.info("Updating nr_measurements stream with %s measurements", nr_measurements)
            yield sse_pack(event_id, "delta", nr_measurements)
        else:
            skipped += 1


@bottle.get("/api/v3/measurements/<metric_uuid>", authentication_required=False)
def get_measurements(metric_uuid: MetricId, database: Database) -> dict:
    """Return the measurements for the metric."""
    metric_uuid = cast(MetricId, metric_uuid.split("&")[0])
    return dict(measurements=list(measurements_by_metric(database, metric_uuid, max_iso_timestamp=report_date_time())))
