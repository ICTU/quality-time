"""Database initialization."""

import os

import pymongo
from pymongo import database

DEFAULT_DATABASE_URL = "mongodb://root:root@localhost:27017"


def client() -> pymongo.MongoClient:  # pragma: no feature-test-cover
    """Return a pymongo client."""
    database_url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    return pymongo.MongoClient(database_url)


def database_connection() -> database.Database:  # pragma: no feature-test-cover
    """Return a pymongo database."""
    return client()["quality_time_db"]
