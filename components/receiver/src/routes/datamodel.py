"""Datamodel routes."""

import bottle
from pymongo.database import Database

from database.datamodels import latest_datamodel


@bottle.get("/datamodel")
def get_datamodel(database: Database):
    """Return the data model."""
    return latest_datamodel(database)
