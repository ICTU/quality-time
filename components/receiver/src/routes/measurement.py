"""Measurement routes."""

from typing import Dict

import bottle
from pymongo.database import Database

from database.measurements import latest_measurement, insert_new_measurement, update_measurement_end


@bottle.post("/measurements")
def post_measurement(database: Database) -> Dict:
    """Put the measurement in the database."""
    measurement = dict(bottle.request.json)
    latest = latest_measurement(database, measurement["metric_uuid"])
    if latest:
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
    return insert_new_measurement(database, measurement)
