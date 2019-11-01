"""Data model routes."""

from pymongo.database import Database
import bottle

from database.datamodels import latest_datamodel
from server_utilities.functions import report_date_time


@bottle.get("/api/v1/datamodel")
def get_datamodel(database: Database):
    """Return the data model."""
    return latest_datamodel(database, report_date_time())
