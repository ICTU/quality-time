"""Test the sessions."""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from database import sessions
from utils.type import SessionId, User

from ..fixtures import JOHN, JENNY


class SessionsTest(unittest.TestCase):
    """Unit tests for sessions class."""

    def setUp(self):
        """Override to set up the database."""
        self.database = Mock()
        self.database.reports_overviews.find_one.return_value = dict(_id="id")

    def create_session(self, session_expiration_datetime=None):
        """Create a fake session in the mock database."""
        session_expiration_datetime = session_expiration_datetime or datetime.now() + timedelta(seconds=5)
        session = JOHN | dict(session_id="5", session_expiration_datetime=session_expiration_datetime)
        self.database.sessions.find_one.return_value = session

    def test_upsert(self):
        """Test upsert function."""
        self.assertIsNone(
            sessions.upsert(
                database=self.database,
                user=User(JENNY["user"], JENNY["email"], JENNY["common_name"]),
                session_id=SessionId("6"),
                session_expiration_datetime=datetime(2019, 10, 18, 19, 22, 5, 99),
            )
        )
        self.database.sessions.replace_one.assert_called_with(
            {"user": JENNY["user"]},
            JENNY | dict(session_id="6", session_expiration_datetime=datetime(2019, 10, 18, 19, 22, 5, 99)),
            upsert=True,
        )

    def test_delete_session(self):
        """Test delete function."""
        self.assertIsNone(sessions.delete(database=self.database, session_id=SessionId("5")))
        self.database.sessions.delete_one.assert_called_with({"session_id": "5"})

    @patch("bottle.request")
    def test_user(self, bottle_mock):
        """Test user function."""
        bottle_mock.get_cookie.return_value = 4
        self.create_session()
        self.assertEqual(
            User(JOHN["user"], JOHN["email"], JOHN["common_name"]),
            sessions.find_user(database=self.database),
        )
        self.database.sessions.find_one.assert_called_with({"session_id": 4})
