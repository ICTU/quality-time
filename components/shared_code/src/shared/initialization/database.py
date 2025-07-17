"""Database initialization."""

import contextlib
import os
from typing import TYPE_CHECKING

import pymongo
from pymongo import database

if TYPE_CHECKING:
    from collections.abc import Generator


@contextlib.contextmanager
def mongo_client() -> Generator[pymongo.MongoClient]:  # pragma: no feature-test-cover
    """Return a pymongo client."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        db_user = os.environ.get("DATABASE_USERNAME", "root")
        db_pass = os.environ.get("DATABASE_PASSWORD", "root")
        db_host = os.environ.get("DATABASE_HOST", "localhost")
        db_port = os.environ.get("DATABASE_PORT", "27017")
        database_url = f"mongodb://{db_user}:{db_pass}@{db_host}:{db_port}"

    client: pymongo.MongoClient = pymongo.MongoClient(database_url)
    try:
        yield client
    finally:
        client.close()


def get_database(client: pymongo.MongoClient, database_name: str = "quality_time_db") -> database.Database:
    """Return one Mongo database."""
    return client.get_database(database_name)
