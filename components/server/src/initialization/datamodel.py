"""Datamodel loader."""

import json
import logging
import os.path
import pathlib

from pymongo.database import Database

from database.datamodels import insert_new_datamodel, latest_datamodel


def import_datamodel(database: Database) -> None:
    """Read the data model and store it in the database."""
    datamodel_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)), "..", "data", "datamodel.json")
    with open(datamodel_path) as json_datamodel:
        data_model = json.load(json_datamodel)
    latest = latest_datamodel(database)
    if latest:
        del latest["timestamp"]
        del latest["_id"]
        if data_model == latest:
            logging.info("Skipping loading the datamodel; it is unchanged")
            return
    insert_new_datamodel(database, data_model)
    logging.info("Datamodel loaded")
