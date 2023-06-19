"""Database initialization."""

import os

import pymongo

DEFAULT_DATABASE_URL = "mongodb://root:root@localhost:27017"


def client(url: str | None = DEFAULT_DATABASE_URL) -> pymongo.MongoClient:  # pragma: no feature-test-cover
    """Return a pymongo client."""
    database_url = os.environ.get("DATABASE_URL", url)
    return pymongo.MongoClient(database_url)


def database_connection(
    url: str | None = DEFAULT_DATABASE_URL,
) -> pymongo.database.Database:  # pragma: no feature-test-cover
    """Return a pymongo database."""
    db_client = client(url)
    return db_client["quality_time_db"]
