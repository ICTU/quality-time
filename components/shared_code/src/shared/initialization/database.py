"""Database initialization."""

import logging

import pymongo

from shared.utils.env import getenv


def client() -> pymongo.MongoClient:  # pragma: no feature-test-cover
    """Return a pymongo client."""
    # DATABASE_URL is deprecated, use the new environment variables if DATABASE_URL is not set
    if database_url := getenv("DATABASE_URL"):
        logging.warning(
            "DATABASE_URL is deprecated, please use DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, "
            "and DATABASE_PORT instead.",
        )
    else:
        user = getenv("DATABASE_USER")
        password = getenv("DATABASE_PASSWORD")
        host = getenv("DATABASE_HOST")
        port = getenv("DATABASE_PORT")
        database_url = f"mongodb://{user}:{password}@{host}:{port}"
    return pymongo.MongoClient(database_url)


def database_connection() -> pymongo.database.Database:  # pragma: no feature-test-cover
    """Return a pymongo database."""
    db_client = client()
    return db_client["quality_time_db"]
