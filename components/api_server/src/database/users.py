"""Users collection."""

from pymongo.database import Database

from utils.type import User


def upsert_user(database: Database, user: User) -> None:
    """Update the existing user or insert a new one."""
    database.users.replace_one({"username": user.username}, dict(user.to_dict()), upsert=True)


def get_user(database: Database, username: str) -> User | None:
    """Get a user, given a username."""
    user_dict = database.users.find_one({"username": username}, {"_id": False})
    return None if user_dict is None else User(**user_dict)
