"""Changelog routes."""

import bottle
from pymongo.database import Database

from database import measurements, reports


@bottle.get("/report/<report_uuid>/changelog/<nr_changes>")
def get_changelog(report_uuid: str, nr_changes: str, database: Database):
    """Return the recent most _nr_changes changes from the changelog."""
    limit = int(nr_changes)
    changes = [dict(delta=change["delta"], timestamp=change["start"])
               for change in measurements.changelog(database, report_uuid, limit)]
    changes.extend([dict(delta=change["delta"], timestamp=change["timestamp"])
                    for change in reports.changelog(database, report_uuid, limit)])
    return dict(changelog=sorted(changes, reverse=True, key=lambda change: change["timestamp"])[:limit])
