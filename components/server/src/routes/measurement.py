"""Measurement routes."""

import logging
import time
from collections.abc import Iterator
from datetime import datetime
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
from server_utilities.functions import days_ago, find_one, iso_timestamp, report_date_time
from server_utilities.type import MetricId, SourceId


@bottle.post("/internal-api/v3/measurements")
def post_measurement(database: Database) -> dict:
    """Put the measurement in the database."""
    measurement_data = dict(bottle.request.json)
    metric_uuid = measurement_data["metric_uuid"]
    if not (metric_data := latest_metric(database, metric_uuid)):  # pylint: disable=superfluous-parens
        return dict(ok=False)  # Metric does not exist, must've been deleted while being measured
    data_model = latest_datamodel(database)
    metric = Metric(data_model, metric_data)
    measurement = Measurement(metric, measurement_data)
    if latest := latest_measurement(database, metric_uuid, metric):
        measurement.set_previous_measurement(latest)
        latest_successful = latest_successful_measurement(database, metric_uuid, metric)
        latest_sources = latest["sources"] if latest_successful is None else latest_successful["sources"]
        copy_entity_user_data(latest_sources, measurement["sources"])
        if not debt_target_expired(metric, latest) and latest["sources"] == measurement["sources"]:
            # If the new measurement is equal to the previous one, merge them together
            update_measurement_end(database, latest["_id"])
            return dict(ok=True)
    return insert_new_measurement(database, measurement)


def copy_entity_user_data(old_sources, new_sources) -> None:
    """Copy the entity user data from the old sources to the new sources."""
    for new_source in new_sources:
        old_source = find_one(old_sources, new_source["source_uuid"], lambda source: SourceId(source["source_uuid"]))
        if old_source:
            copy_source_entity_user_data(old_source, new_source)


def copy_source_entity_user_data(old_source, new_source) -> None:
    """Copy the user entity data of the source."""
    new_entity_keys = {entity["key"] for entity in new_source.get("entities", [])}
    # Sometimes the key Quality-time generates for entities needs to change, e.g. when it turns out not to be
    # unique. Create a mapping of old keys to new keys so we can move the entity user data to the new keys
    changed_entity_keys = {
        entity["old_key"]: entity["key"] for entity in new_source.get("entities", []) if "old_key" in entity
    }
    # Copy the user data of entities, keeping 'orphaned' entity user data around for a while in case the entity
    # returns in a later measurement:
    max_days_to_keep_orphaned_entity_user_data = 21
    for entity_key, attributes in old_source.get("entity_user_data", {}).items():
        entity_key = changed_entity_keys.get(entity_key, entity_key)
        if entity_key in new_entity_keys:
            if "orphaned_since" in attributes:
                del attributes["orphaned_since"]  # The entity returned, remove the orphaned since date/time
        else:
            if "orphaned_since" in attributes:
                days_since_orphaned = days_ago(datetime.fromisoformat(attributes["orphaned_since"]))
                if days_since_orphaned > max_days_to_keep_orphaned_entity_user_data:  # pragma: no cover-behave
                    continue  # Don't copy this user data, it has been orphaned too long
            else:
                # The entity user data refers to a disappeared entity. Keep it around in case the entity
                # returns, but also set the current date/time so we can eventually remove the user data.
                attributes["orphaned_since"] = iso_timestamp()
        new_source.setdefault("entity_user_data", {})[entity_key] = attributes


def debt_target_expired(metric: Metric, measurement) -> bool:
    """Return whether the technical debt target is expired.

    Technical debt can expire because it was turned off or because the end date passed.
    """
    any_debt_target = any(measurement.get(scale, {}).get("debt_target") is not None for scale in metric.scales())
    if not any_debt_target:
        return False
    return metric.accept_debt_expired()


@bottle.post("/api/v3/measurement/<metric_uuid>/source/<source_uuid>/entity/<entity_key>/<attribute>")
def set_entity_attribute(
    metric_uuid: MetricId, source_uuid: SourceId, entity_key: str, attribute: str, database: Database
) -> dict:
    """Set an entity attribute."""
    data = SourceData(latest_datamodel(database), latest_reports(database), source_uuid)
    metric = Metric(data.datamodel, data.metric)
    old_measurement = cast(Measurement, latest_measurement(database, metric_uuid, metric))
    new_measurement = Measurement.copy_from(old_measurement)
    source = [s for s in new_measurement["sources"] if s["source_uuid"] == source_uuid][0]
    entity = [e for e in source["entities"] if e["key"] == entity_key][0]
    entity_description = "/".join([entity[key] for key in entity.keys() if key not in ("key", "url")])
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


@bottle.get("/api/v3/nr_measurements")
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


@bottle.get("/api/v3/measurements/<metric_uuid>")
def get_measurements(metric_uuid: MetricId, database: Database) -> dict:
    """Return the measurements for the metric."""
    metric_uuid = cast(MetricId, metric_uuid.split("&")[0])
    return dict(measurements=list(measurements_by_metric(database, metric_uuid, max_iso_timestamp=report_date_time())))
