"""Data model loader."""

import json
import logging
import pathlib

from pymongo.database import Database

from database.datamodels import insert_new_datamodel, latest_datamodel


# The coverage measurement of the behave feature tests is unstable. Most of the time it reports the last two lines
# on the import_datamodel method as covered, sometimes not. It's unclear why. To prevent needless checking, coverage
# measurement for this method has been turned off.

def import_datamodel(database: Database) -> None:  # pragma: no-cover behave
    """Read the data model and store it in the database."""
    data_model_path = pathlib.Path(__file__).resolve().parent.parent / "data" / "datamodel.json"
    with data_model_path.open() as json_data_model:
        data_model = json.load(json_data_model)
    if latest := latest_datamodel(database):
        del latest["timestamp"]
        del latest["_id"]
        if data_model == latest:
            logging.info("Skipping loading the data model; it is unchanged")
            return
    insert_new_datamodel(database, data_model)
    logging.info("Data model loaded")
