"""Data model routes."""

import bottle
from typing import TYPE_CHECKING

from shared.utils.functions import md5_hash

from database.datamodels import latest_datamodel
from utils.functions import report_date_time

if TYPE_CHECKING:
    from pymongo.database import Database


@bottle.get("/api/internal/datamodel", authentication_required=False)
def get_data_model(database: Database):
    """Return the data model."""
    data_model = latest_datamodel(database, report_date_time())
    if data_model:
        md5 = md5_hash(data_model["timestamp"])
        if md5 == bottle.request.headers.get("If-None-Match"):
            bottle.abort(304)  # Data model unchanged
        bottle.response.set_header("ETag", md5)
    return data_model
