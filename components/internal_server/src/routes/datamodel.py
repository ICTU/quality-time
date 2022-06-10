"""Data model routes."""

import bottle
from pymongo.database import Database

from shared.routes import get_data_model as get_data_model_implementation


@bottle.get("/api/datamodel", authentication_required=False)
def get_data_model(database: Database):
    """Return the data model."""
    return get_data_model_implementation(database)  # pragma: no cover
