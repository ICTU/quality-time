"""Data model loader."""

import json
import logging

from pymongo.database import Database

from external.data_model import DATA_MODEL_JSON
from external.database.datamodels import insert_new_datamodel, latest_datamodel


def import_datamodel(database: Database) -> None:
    """Store the data model in the database."""
    data_model = json.loads(DATA_MODEL_JSON)
    if latest := latest_datamodel(database):
        del latest["timestamp"]
        del latest["_id"]
        if data_model == latest:  # pragma: no cover-behave
            logging.info("Skipping loading the data model; it is unchanged")
            return
    insert_new_datamodel(database, data_model)
    logging.info("Data model loaded")
