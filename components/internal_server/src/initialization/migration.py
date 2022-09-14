"""Database migration code."""

from datetime import datetime
import logging

from pymongo.database import Database
from pymongo.operations import DeleteMany, UpdateOne
import pymongo


SCALES = ("count", "percentage", "version_number")  # All scales Quality-time has ever supported
OLD_TO_NEW = [("start", pymongo.ASCENDING)]


def merge_unmerged_measurements(database: Database) -> None:
    """Due to a bug, measurements were not properly merged. Clean up by merging measurements where possible.

    This migration code was added when the most recent version of Quality-time was 4.3.0.
    Bug issue: https://github.com/ICTU/quality-time/issues/4554
    Cleanup issue: https://github.com/ICTU/quality-time/issues/4556.
    """
    start = datetime.now()
    logging.info("Starting migration 'merge unmerged measurements' at %s", start)
    nr_measurements = int(database.measurements.estimated_document_count())
    metric_uuids = database.measurements.distinct("metric_uuid")
    nr_metrics = len(metric_uuids)
    logging.info("Measurements collection has %d measurements for %d metrics", nr_measurements, nr_metrics)
    for index, metric_uuid in enumerate(metric_uuids):
        logging.info("Merging measurements for metric %s (%d/%d)", metric_uuid, index + 1, nr_metrics)
        measurements_to_update = {}  # Mapping of Mongo object ids of measurements to their new end-timestamp
        measurements_to_delete = set()  # The measurements that have been merged into a previous measurement
        measurement_to_potentially_update = {}  # The current measurement that may get newer measurements merged into it
        for measurement in database.measurements.find(dict(metric_uuid=metric_uuid), sort=OLD_TO_NEW):
            if equal(measurement_to_potentially_update, measurement):
                measurements_to_update[measurement_to_potentially_update["_id"]] = measurement["end"]
                measurements_to_delete.add(measurement["_id"])
            else:
                measurement_to_potentially_update = measurement
        updates = [
            UpdateOne({"_id": object_id}, update=dict(end=end)) for object_id, end in measurements_to_update.items()
        ]
        deletes = DeleteMany({"_id": {"$in": measurements_to_delete}})
        database.measurements.bulk_write(updates + [deletes])
        logging.info("Updated: %d, deleted: %s", len(measurements_to_update), len(measurements_to_delete))
    stop = datetime.now()
    logging.info("Finished migration 'merge unmerged measurements' at %s, took %s", stop, stop - start)


def equal(measurement1, measurement2) -> bool:
    """Return whether the measurements are equal."""
    scales_equal = all(measurement1.get(scale) == measurement2.get(scale) for scale in SCALES)
    issues_statuses_equal = measurement1.get("issue_status") == measurement2.get("issue_status")
    sources_equal = measurement1.get("sources") == measurement2.get("sources")
    return scales_equal and issues_statuses_equal and sources_equal
