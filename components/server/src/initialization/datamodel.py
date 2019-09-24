"""Data model loader."""

import json
import logging
import os.path
import pathlib

from pymongo.database import Database

from database.datamodels import insert_new_datamodel, latest_datamodel


def import_datamodel(database: Database) -> None:
    """Read the data model and store it in the database."""
    data_model_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)), "..", "data", "datamodel.json")
    with open(data_model_path) as json_data_model:
        data_model = json.load(json_data_model)
    latest = latest_datamodel(database)
    if latest:
        del latest["timestamp"]
        del latest["_id"]
        if data_model == latest:
            logging.info("Skipping loading the data model; it is unchanged")
            return
    insert_new_datamodel(database, data_model)
    logging.info("Data model loaded")
