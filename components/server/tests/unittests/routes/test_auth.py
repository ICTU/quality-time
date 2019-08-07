"""Unit tests for the authorization routes."""

import unittest
from unittest.mock import Mock, patch

import bottle
import ldap  # pylint: disable=import-error

from src.routes import auth


class LoginTests(unittest.TestCase):
    """Unit tests for the login route."""
    def setUp(self):
        self.database = Mock()
        self.ldap_server = Mock()
        self.ldap_server.search_s.return_value = [
            ('cn=John Doe,ou=users,dc=example,dc=org', {'cn': [b'John Doe'], 'uid': [b'jodoe']})
        ]

    def tearDown(self):
        bottle.response._cookies = None  # pylint: disable=protected-access

    def test_successful_login_localhost_uid(self):
        """Test successful login on localhost."""
        resp1 = Mock(json=dict(username="admin", password="admin"))
        resp2 = Mock(json=dict(username="jodoe", password="secret"))

        with patch("os.environ.get", Mock(return_value="http://localhost:5001")):
            with patch("bottle.request", return_value=[resp1, resp2]):
                with patch("ldap.initialize", return_value=self.ldap_server):
                    self.assertEqual(dict(ok=True), auth.login(self.database))
        cookie = str(bottle.response._cookies)  # pylint: disable=protected-access
        self.assertTrue(cookie.startswith("Set-Cookie: session_id="))
        self.assertFalse("domain=" in cookie.lower())

    def test_successful_login_localhost_cn(self):
        """Test successful login on localhost."""
        resp1 = Mock(json=dict(username="admin", password="admin"))
        resp2 = Mock(json=dict(username="John Doe", password="secret"))

        with patch("os.environ.get", Mock(return_value="http://localhost:5001")):
            with patch("bottle.request", return_value=[resp1, resp2]):
                with patch("ldap.initialize", return_value=self.ldap_server):
                    self.assertEqual(dict(ok=True), auth.login(self.database))
        cookie = str(bottle.response._cookies)  # pylint: disable=protected-access
        self.assertTrue(cookie.startswith("Set-Cookie: session_id="))
        self.assertFalse("domain=" in cookie.lower())

    def test_unsuccessful_login_localhost_cn(self):
        """Test successful login on localhost."""
        resp1 = Mock(json=dict(username="admin", password="admin"))
        resp2 = Mock(json=dict(username="wrong", password="wrong"))

        self.ldap_server.search_s.side_effect = ldap.INVALID_CREDENTIALS

        with patch("os.environ.get", Mock(return_value="http://localhost:5001")):
            with patch("bottle.request", return_value=[resp1, resp2]):
                with patch("ldap.initialize", return_value=self.ldap_server):
                    self.assertEqual(dict(ok=False), auth.login(self.database))

    def test_failed_login(self):
        """Test failed login."""
        self.ldap_server.simple_bind_s.side_effect = ldap.INVALID_CREDENTIALS  # pylint: disable=no-member

        resp1 = Mock(json=dict(username="admin", password="admin"))
        
        with patch("logging.warning", Mock()):
            with patch("bottle.request", return_value=resp1):
                with patch("ldap.initialize", return_value=self.ldap_server):
                    self.assertEqual(dict(ok=False), auth.login(self.database))


class LogoutTests(unittest.TestCase):
    """Unit tests for the logout route."""
    def test_logout(self):
        """Test successful logout."""
        database = Mock()
        self.assertEqual(dict(ok=True), auth.logout(database))
