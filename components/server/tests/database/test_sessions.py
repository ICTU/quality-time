"""Test the sessions."""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from database import sessions
from server_utilities.type import SessionId


class SessionsTest(unittest.TestCase):
    """Unit tests for sessions class."""

    def setUp(self):
        """Override to set up the database."""
        self.database = Mock()
        self.database.reports_overviews.find_one.return_value = dict(_id="id")

    def create_session(self, session_expiration_datetime=None):
        """Create a fake session in the mock database."""
        session_expiration_datetime = session_expiration_datetime or datetime.now() + timedelta(seconds=5)
        session = dict(
            user="jodoe",
            email="jodoe@example.org",
            session_id="5",
            session_expiration_datetime=session_expiration_datetime,
        )
        self.database.sessions.find_one.return_value = session

    def test_upsert(self):
        """Test upsert function."""
        self.assertIsNone(
            sessions.upsert(
                database=self.database,
                username="jadoe",
                email="jadoe@example.org",
                session_id=SessionId("6"),
                session_expiration_datetime=datetime(2019, 10, 18, 19, 22, 5, 99),
            )
        )
        self.database.sessions.update.assert_called_with(
            {"user": "jadoe"},
            {
                "user": "jadoe",
                "email": "jadoe@example.org",
                "session_id": "6",
                "session_expiration_datetime": datetime(2019, 10, 18, 19, 22, 5, 99),
            },
            upsert=True,
        )

    def test_delete_session(self):
        """Test delete function."""
        self.assertIsNone(sessions.delete(database=self.database, session_id=SessionId("5")))
        self.database.sessions.delete_one.assert_called_with({"session_id": "5"})

    def test_valid_session(self):
        """Test that a non-expired session with the required roles is valid."""
        self.create_session()
        self.assertTrue(sessions.valid(database=self.database, session_id=SessionId("5")))
        self.database.sessions.find_one.assert_called_with({"session_id": "5"})

    def test_expired_session(self):
        """Test that an expired session with the required roles is invalid."""
        self.create_session(session_expiration_datetime=datetime.min)
        self.assertFalse(sessions.valid(database=self.database, session_id=SessionId("5")))
        self.database.sessions.find_one.assert_called_with({"session_id": "5"})

    def test_no_session_with_id(self):
        """Test that a session that is not found is invalid."""
        self.database.sessions.find_one.return_value = None
        self.assertFalse(sessions.valid(database=self.database, session_id=SessionId("5")))
        self.database.sessions.find_one.assert_called_with({"session_id": "5"})

    def test_authorized_session_without_editors(self):
        """Test that a session is authorized when no editors are defined and the session is valid."""
        self.create_session()
        self.assertTrue(sessions.authorized(database=self.database, session_id=SessionId("5")))
        self.database.sessions.find_one.assert_called_with({"session_id": "5"})

    def test_authorized_session_with_editors(self):
        """Test that a session is authorized when editors are defined and the session's user is an editor."""
        self.database.reports_overviews.find_one.return_value = dict(_id="id", editors=["jodoe@example.org"])
        self.create_session()
        self.assertTrue(sessions.authorized(database=self.database, session_id=SessionId("5")))
        self.database.sessions.find_one.assert_called_with({"session_id": "5"})

    def test_unauthorized_session(self):
        """Test that a session is unauthorized when editors are defined and the session's user is not an editor."""
        self.database.reports_overviews.find_one.return_value = dict(_id="id", editors=["jadoe@example.org"])
        self.create_session()
        self.assertFalse(sessions.authorized(database=self.database, session_id=SessionId("5")))
        self.database.sessions.find_one.assert_called_with({"session_id": "5"})

    def test_unauthorized_without_session(self):
        """Test that a session is unauthorized if there's no valid session."""
        self.database.sessions.find_one.return_value = None
        self.assertFalse(sessions.authorized(database=self.database, session_id=SessionId("5")))
        self.database.sessions.find_one.assert_called_with({"session_id": "5"})

    @patch("bottle.request")
    def test_user(self, bottle_mock):
        """Test user function."""
        bottle_mock.get_cookie.return_value = 4
        self.create_session()
        self.assertEqual("jodoe", sessions.user(database=self.database)["user"])
        self.database.sessions.find_one.assert_called_with({"session_id": 4})
