"""Datamodel loader."""

import json
import logging

from pymongo.database import Database

from database.datamodels import insert_new_datamodel, latest_datamodel


def import_datamodel(database: Database) -> None:
    """Read the data model and store it in the database."""
    with open("src/data/datamodel.json") as json_datamodel:
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
