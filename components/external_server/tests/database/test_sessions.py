"""Test the sessions."""

from datetime import datetime, UTC

from shared.utils.type import SessionId, User

from database import sessions

from tests.base import DatabaseTestCase
from tests.fixtures import JENNY


class SessionsTest(DatabaseTestCase):
    """Unit tests for sessions class."""

    def setUp(self):
        """Override to set up the database."""
        super().setUp()
        self.database.reports_overviews.find_one.return_value = {"_id": "id"}
        self.database.sessions.find_one.return_value = {"_id": "session_id"}

    def test_upsert(self):
        """Test upsert function."""
        self.assertIsNone(
            sessions.upsert(
                database=self.database,
                user=User(JENNY["user"], JENNY["email"], JENNY["common_name"]),
                session_id=SessionId("6"),
                session_expiration_datetime=datetime(2019, 10, 18, 19, 22, 5, 99, tzinfo=UTC),
            ),
        )
        self.database.sessions.replace_one.assert_called_with(
            {"user": JENNY["user"]},
            JENNY
            | {
                "session_id": "6",
                "session_expiration_datetime": datetime(2019, 10, 18, 19, 22, 5, 99, tzinfo=UTC),
            },
            upsert=True,
        )

    def test_delete_session(self):
        """Test delete function."""
        self.assertIsNone(sessions.delete(database=self.database, session_id=SessionId("5")))
        self.database.sessions.delete_one.assert_called_with({"session_id": "5"})

    def test_get(self):
        """Test get session."""
        session = sessions.get(self.database, "session_id")
        self.assertDictEqual(session, {"_id": "session_id"})
        self.database.sessions.find_one.assert_called_once_with({"session_id": "session_id"})
