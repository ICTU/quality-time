"""Database migration code."""

from datetime import datetime
import logging

from pymongo.database import Database
from pymongo.operations import DeleteMany, UpdateOne
import pymongo


SCALES = ("count", "percentage", "version_number")  # All scales Quality-time has ever supported
OLD_TO_NEW = [("start", pymongo.ASCENDING)]
MeasurementJSON = dict[str, dict]


def merge_unmerged_measurements(database: Database) -> None:
    """Due to a bug, measurements were not properly merged. Clean up by merging measurements where possible.

    This migration code was added when the most recent version of Quality-time was 4.3.0.
    Bug issue: https://github.com/ICTU/quality-time/issues/4554
    Cleanup issue: https://github.com/ICTU/quality-time/issues/4556.
    """
    start = datetime.now()
    logging.info("Starting migration 'merge unmerged measurements' at %s", start)
    total_nr_measurements = int(database.measurements.estimated_document_count())
    metric_uuids = database.measurements.distinct("metric_uuid")
    nr_metrics = len(metric_uuids)
    logging.info("Measurements collection has %d measurements for %d metrics", total_nr_measurements, nr_metrics)
    for index, metric_uuid in enumerate(metric_uuids):  # pragma: no cover-behave
        logging.info("Merging measurements for metric %s (%d/%d)", metric_uuid, index + 1, nr_metrics)
        nr_updated, nr_deleted, nr_measurements = _merge_unmerged_measurements_for_metric(database, metric_uuid)
        if nr_updated > 0 or nr_deleted > 0:
            percentage_updated = round(100 * nr_updated / nr_measurements)
            percentage_deleted = round(100 * nr_deleted / nr_measurements)
            logging.info(
                "...updated %d (%d%%) measurements and deleted %d (%d%%) measurements of %d measurements",
                nr_updated,
                percentage_updated,
                nr_deleted,
                percentage_deleted,
                nr_measurements,
            )
    stop = datetime.now()
    logging.info("Finished migration 'merge unmerged measurements' at %s, took %s", stop, stop - start)


def _merge_unmerged_measurements_for_metric(
    database: Database, metric_uuid: str
) -> tuple[int, int, int]:  # pragma: no cover-behave
    """Merge the unmerged measurements of the specified metric.

    Returns the number of updates, deletes, and total number of measurements.
    """
    updates = {}  # Mongo object ids (keys) of measurements that will be updated with a new end-timestamp (values)
    deletes = []  # The Mongo object ids of measurements that have been merged and will be deleted
    current: MeasurementJSON = {}  # The current measurement that will be updated if it is equal to a later measurement
    nr_measurements = 0
    for measurement in database.measurements.find(dict(metric_uuid=metric_uuid), sort=OLD_TO_NEW):
        nr_measurements += 1
        if _equal(current, measurement):
            updates[current["_id"]] = measurement["end"]
            deletes.append(measurement["_id"])
        else:
            current = measurement
    mongo_operations: list[UpdateOne | DeleteMany] = []
    mongo_operations.extend(
        UpdateOne({"_id": object_id}, {"$set": dict(end=end)}) for object_id, end in updates.items()
    )
    mongo_operations.append(DeleteMany({"_id": {"$in": deletes}}))
    database.measurements.bulk_write(mongo_operations)
    return len(updates), len(deletes), nr_measurements


def _equal(measurement1: MeasurementJSON, measurement2: MeasurementJSON) -> bool:  # pragma: no cover-behave
    """Return whether the measurements are equal."""
    scales_equal = all(measurement1.get(scale) == measurement2.get(scale) for scale in SCALES)
    issues_statuses_equal = measurement1.get("issue_status") == measurement2.get("issue_status")
    sources_equal = measurement1.get("sources") == measurement2.get("sources")
    return scales_equal and issues_statuses_equal and sources_equal
