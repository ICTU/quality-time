"""Reports collection."""

from typing import cast

import pymongo
from pymongo.database import Database

from database.filters import DOES_EXIST

from server_utilities.functions import unique

from ..utils.type import Change


# Sort order:
TIMESTAMP_DESCENDING = [("timestamp", pymongo.DESCENDING)]


def changelog(database: Database, nr_changes: int, **uuids):
    """Return the changelog, narrowed to a single report, subject, metric, or source if so required.

    The uuids keyword arguments may contain report_uuid="report_uuid", and one of subject_uuid="subject_uuid",
    metric_uuid="metric_uuid", and source_uuid="source_uuid".
    """
    projection = {"delta": True, "timestamp": True}
    delta_filter: dict[str, dict | list] = {"delta": DOES_EXIST}
    changes: list[Change] = []
    if not uuids:
        changes.extend(
            database.reports_overviews.find(
                filter=delta_filter, sort=TIMESTAMP_DESCENDING, limit=nr_changes * 2, projection=projection
            )
        )
    old_report_delta_filter = {f"delta.{key}": value for key, value in uuids.items() if value}
    new_report_delta_filter = {"delta.uuids": {"$in": list(uuids.values())}}
    delta_filter["$or"] = [old_report_delta_filter, new_report_delta_filter]
    changes.extend(
        database.reports.find(
            filter=delta_filter, sort=TIMESTAMP_DESCENDING, limit=nr_changes * 2, projection=projection
        )
    )
    changes = sorted(changes, reverse=True, key=lambda change: cast(str, change["timestamp"]))
    # Weed out potential duplicates, because when a user moves items between reports both reports get the same delta
    return list(unique(changes, _get_change_key))[:nr_changes]


def _get_change_key(change: Change) -> str:
    """Return a key for detecting equal changes."""
    description = cast(dict[str, str], change["delta"])["description"]
    changed_uuids = cast(dict[str, list[str]], change["delta"]).get("uuids", [])
    key = f"{change['timestamp']}:{','.join(sorted(changed_uuids))}:{description}"
    return key
