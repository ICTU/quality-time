"""Test the sessions."""

import unittest
from datetime import datetime
from unittest.mock import Mock

from shared.utils.type import SessionId, User

from database import sessions

from ..fixtures import JENNY


class SessionsTest(unittest.TestCase):
    """Unit tests for sessions class."""

    def setUp(self):
        """Override to set up the database."""
        self.database = Mock()
        self.database.reports_overviews.find_one.return_value = dict(_id="id")
        self.database.sessions.find_one.return_value = dict(_id="session_id")

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

    def test_get(self):
        """Test get."""
        session = sessions.get(self.database, "session_id")
        self.assertDictEqual(session, dict(_id="session_id"))
        self.database.sessions.find_one.assert_called_once_with({"session_id": "session_id"})
