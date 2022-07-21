"""Test the sessions."""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from shared.database import sessions

from ...fixtures import JOHN


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

    @patch("bottle.request")
    def test_user(self, bottle_mock):
        """Test user function."""
        bottle_mock.get_cookie.return_value = 4
        self.create_session()
        user = sessions.find_user(database=self.database)
        self.assertEqual(JOHN["user"], user.username)
        self.assertEqual(JOHN["email"], user.email)
        self.assertEqual(JOHN["common_name"], user.common_name)
        self.assertEqual(False, user.verified)
        self.assertEqual("John Doe", user.name())
        self.database.sessions.find_one.assert_called_with({"session_id": 4})
