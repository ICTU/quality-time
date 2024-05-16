"""Database initialization."""

import os

import pymongo
from pymongo import database


def client() -> pymongo.MongoClient:  # pragma: no feature-test-cover
    """Return a pymongo client."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        db_user = os.environ.get("DATABASE_USERNAME", "root")
        db_pass = os.environ.get("DATABASE_PASSWORD", "root")
        db_host = os.environ.get("DATABASE_HOST", "localhost")
        db_port = os.environ.get("DATABASE_PORT", "27017")
        database_url = f"mongodb://{db_user}:{db_pass}@{db_host}:{db_port}"

    return pymongo.MongoClient(database_url)


def database_connection() -> database.Database:  # pragma: no feature-test-cover
    """Return a pymongo database."""
    return client()["quality_time_db"]
