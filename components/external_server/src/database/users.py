"""Users collection."""

from pymongo.database import Database

from shared.utils.type import User


def upsert_user(database: Database, user: User) -> None:
    """Update the existing user or insert a new one."""
    database.users.replace_one(
        dict(username=user.username),
        dict(user.to_dict()),
        upsert=True,
    )


def get_user(database: Database, username: str) -> User | None:
    """Get a user, given a username."""
    user_dict = database.users.find_one({"username": username}, {"_id": False})
    if user_dict is not None:
        return User(**user_dict)
    return None
