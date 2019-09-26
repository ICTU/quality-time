"""Data model routes."""

from pymongo.database import Database
import bottle

from database.datamodels import latest_datamodel
from utilities.functions import report_date_time


@bottle.get("/datamodel")
def get_datamodel(database: Database):
    """Return the data model."""
    return latest_datamodel(database, report_date_time())
