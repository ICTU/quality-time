"""Datamodel routes."""

import bottle

from ..database.datamodels import latest_datamodel
from ..util import report_date_time


@bottle.get("/datamodel")
def get_datamodel(database):
    """Return the data model."""
    return latest_datamodel(report_date_time(), database)
