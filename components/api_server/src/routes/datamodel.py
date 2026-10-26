"""Data model routes."""

import json

import bottle
from typing import TYPE_CHECKING, Final, cast

from shared.utils.functions import md5_hash

from database.datamodels import latest_datamodel
from utils.functions import report_date_time

if TYPE_CHECKING:
    from pymongo.database import Database

# Data models stored before configuration settings were moved from code to the data model don't have them. Insert the
# configuration that applied when those data models were stored. Don't change these values when the configuration in
# the shared data model changes. When moving more configuration settings from code to the data model, add them here with
# the value they had in the code. Entirely new configuration settings only need to be added to the shared data model,
# in shared_data_model/meta/config.py (the setting) and shared_data_model/config.py (its value).
CONFIG_OF_DATA_MODELS_WITHOUT_CONFIG: Final = {
    "desired_response_times": {
        "debt_target_met": 60,
        "near_target_met": 21,
        "target_not_met": 7,
        "unknown": 3,
        "confirmed": 180,
        "false_positive": 180,
        "wont_fix": 180,
        "fixed": 7,
    },
}


@bottle.get("/api/internal/datamodel", authentication_required=False)
def get_data_model(database: Database):
    """Return the data model."""
    data_model = latest_datamodel(database, report_date_time())
    if data_model:
        data_model["config"] = CONFIG_OF_DATA_MODELS_WITHOUT_CONFIG | data_model.get("config", {})
        # Include the config in the ETag so clients that cached a data model before the config was inserted get the
        # data model with config:
        md5 = md5_hash(data_model["timestamp"] + json.dumps(data_model["config"], sort_keys=True))
        if md5 == cast(dict, bottle.request.headers).get("If-None-Match"):
            bottle.abort(304)  # Data model unchanged
        bottle.response.set_header("ETag", md5)
    return data_model
