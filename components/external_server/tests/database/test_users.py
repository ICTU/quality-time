"""Test the sessions."""

from shared.utils.type import User

from database import users

from tests.base import DatabaseTestCase


class UsersTest(DatabaseTestCase):
    """Unit tests for user database functions."""

    def setUp(self):
        """Extend to set up the users collection."""
        super().setUp()
        self.database.users.find_one.return_value = {"username": "username"}

    def test_upsert(self):
        """Test upsert function."""
        self.assertIsNone(
            users.upsert_user(
                database=self.database,
                user=User(username="test", email="info@test.com"),
            ),
        )
        self.database.users.replace_one.assert_called_with(
            {"username": "test"},
            {"username": "test", "email": "info@test.com", "common_name": "", "settings": {}},
            upsert=True,
        )

    def test_get(self):
        """Test get user."""
        user = users.get_user(self.database, "username")
        self.assertDictEqual(user.to_dict(), {"username": "username", "email": "", "common_name": "", "settings": {}})
        self.database.users.find_one.assert_called_once_with({"username": "username"}, {"_id": False})

    def test_get_nonexisting(self):
        """Should return None when user doesn't exist."""
        self.database.users.find_one.return_value = None
        user = users.get_user(self.database, "does not exist")
        self.assertIsNone(user)
