"""API for the datamodel."""

import bottle


@bottle.get("/datamodel")
def get_datamodel(database):
    """Return the data model."""
    datamodel = database.datamodel.find_one({})
    datamodel["_id"] = str(datamodel["_id"])
    return datamodel


@bottle.get("/datamodel/<data_type_collection>/<data_type_key>")
def get_datamodel_data_type(data_type_collection: str, data_type_key: str, database):
    """Return the data type."""
    datamodel = database.datamodel.find_one({})
    return datamodel[data_type_collection][data_type_key]
