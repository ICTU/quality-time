"""Data model loader."""

import json
from typing import TYPE_CHECKING

from shared_data_model import DATA_MODEL_JSON

from database.datamodels import insert_new_datamodel, latest_datamodel
from utils.log import get_logger

if TYPE_CHECKING:
    from pymongo.database import Database


def import_datamodel(database: Database) -> None:  # pragma: no feature-test-cover
    """Store the data model in the database."""
    logger = get_logger()
    data_model = json.loads(DATA_MODEL_JSON)
    if latest := latest_datamodel(database):
        del latest["timestamp"]
        del latest["_id"]
        if data_model == latest:
            logger.info("Skipping loading the data model; it is unchanged")
            return
    insert_new_datamodel(database, data_model)
    logger.info("Data model loaded")
