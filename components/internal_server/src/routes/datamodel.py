"""Data model routes."""

import bottle
from pymongo.database import Database

from shared.database.datamodels import latest_datamodel
from shared.utils.functions import md5_hash, report_date_time


@bottle.get("/api/v3/datamodel", authentication_required=False)
def get_data_model(database: Database):
    """Return the data model."""
    report_date_string = report_date_time(dict(bottle.request.query).get("report_date"))
    data_model = latest_datamodel(database, report_date_string)
    if data_model:
        md5 = md5_hash(data_model["timestamp"])
        if "W/" + md5 == bottle.request.headers.get("If-None-Match"):  # pylint: disable=no-member
            bottle.abort(304)  # Data model unchanged
        bottle.response.set_header("ETag", md5)
    return data_model
