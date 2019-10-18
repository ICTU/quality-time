"""Test the sessions."""

import unittest
import bottle
from datetime import datetime, timedelta
# from pymongo.database import Database
from unittest.mock import patch, MagicMock

from src.database import sessions

class SessionsTest(unittest.TestCase):
    """Unit tests for sessions class."""

    def test_upsert(self):
        """Test upsert function."""
        db = MagicMock()
        db.sessions = MagicMock()
        db.sessions.update = MagicMock()
        sessions.upsert(database=db, username='un', session_id='5',
                        session_expiration_datetime=datetime(2019, 10, 18, 19, 22, 5, 99))
        db.sessions.update.assert_called_with(
            {'user': 'un'}, {'user': 'un', 'session_id': '5',
                             'session_expiration_datetime': datetime(2019, 10, 18, 19, 22, 5, 99)}, upsert=True)

    def test_delete(self):
        """Test delete function."""
        db = MagicMock()
        db.sessions = MagicMock()
        db.sessions.delete_one = MagicMock()
        sessions.delete(database=db, session_id='5')
        db.sessions.delete_one.assert_called_with({'session_id': '5'})

    def test_valid(self):
        """Test valid function."""
        session_obj = MagicMock()
        session_obj.get = MagicMock(return_value=(datetime.now() + timedelta(seconds=5)))
        db = MagicMock()
        db.sessions = MagicMock()
        db.sessions.find_one = MagicMock(return_value=session_obj)
        self.assertTrue(sessions.valid(database=db, session_id='5'))
        db.sessions.find_one.assert_called_with({'session_id': '5'})

    def test_valid_min_date(self):
        """Test valid function with min date."""
        session_obj = MagicMock()
        session_obj.get = MagicMock(return_value=datetime.min)
        db = MagicMock()
        db.sessions = MagicMock()
        db.sessions.find_one = MagicMock(return_value=session_obj)
        self.assertFalse(sessions.valid(database=db, session_id='5'))
        db.sessions.find_one.assert_called_with({'session_id': '5'})

    def test_valid_session_not_found(self):
        """Test valid function when the session is not found."""
        db = MagicMock()
        db.sessions = MagicMock()
        db.sessions.find_one = MagicMock(return_value=None)
        self.assertFalse(sessions.valid(database=db, session_id='5'))
        db.sessions.find_one.assert_called_with({'session_id': '5'})

    @patch('bottle.request')
    def test_user(self, bottle_mock):
        """Test user function."""
        bottle_mock.get_cookie = MagicMock(return_value=5)
        db = MagicMock()
        db.sessions = MagicMock()
        db.sessions.find_one = MagicMock(return_value={"user": "OK"})

        self.assertEqual('OK', sessions.user(database=db))
        db.sessions.find_one.assert_called_with({'session_id': '5'})
