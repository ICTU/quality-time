"""users collection."""

from pymongo.database import Database

from shared.utils.type import User


def upsert_user(database: Database, user: User) -> None:
    """Update the existing user or insert a new one."""
    database.users.replace_one(
        dict(user=user.username),
        dict(
            user.to_dict()
        ),
        upsert=True,
    )
