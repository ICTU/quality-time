"""Measurements collection."""

import pymongo
from pymongo.database import Database


def changelog(database: Database, nr_changes: int, **uuids):
    """Return the changelog for the measurements belonging to the items with the specific uuids."""
    return database.measurements.find(
        filter={"delta.uuids": {"$in": list(uuids.values())}},
        sort=[("start", pymongo.DESCENDING)],
        limit=nr_changes,
        projection=["delta", "start"],
    )


def count_measurements(database: Database) -> int:
    """Return the number of measurements."""
    return int(database.measurements.estimated_document_count())
