"""Database initialization."""

import logging
import os

import pymongo  # pylint: disable=wrong-import-order
from pymongo.database import Database


def init_database() -> Database:
    """Initialize the database connection and contents."""
    database_url = os.environ.get("DATABASE_URL", "mongodb://root:root@localhost:27017")
    database = pymongo.MongoClient(database_url).quality_time_db
    logging.info("Connected to database: %s", database)
    nr_measurements = database.measurements.count_documents({})
    logging.info("Database has %d measurement documents", nr_measurements)
    return database
