"""Unit tests for the authorization routes."""

import unittest
from unittest.mock import Mock, patch

import bottle
import ldap  # pylint: disable=import-error

from src.routes import auth


class LoginTests(unittest.TestCase):
    """Unit tests for the login route."""
    def setUp(self):
        self.request = Mock()
        self.request.json = dict(username="user", password="pass")
        self.database = Mock()
        self.ldap_server = Mock()

    def tearDown(self):
        bottle.response._cookies = None  # pylint: disable=protected-access

    def test_successful_login(self):
        """Test successful login."""
        with patch("os.environ.get", Mock(return_value="http://www.quality-time.my-org.org:5001")):
            with patch("bottle.request", self.request):
                with patch("ldap.initialize", return_value=self.ldap_server):
                    self.assertEqual(dict(ok=True), auth.login(self.database))
        cookie = str(bottle.response._cookies)  # pylint: disable=protected-access
        self.assertTrue(cookie.startswith("Set-Cookie: session_id="))
        self.assertTrue("domain=" in cookie.lower())

    def test_successful_login_localhost(self):
        """Test successful login on localhost."""
        with patch("os.environ.get", Mock(return_value="http://localhost:5001")):
            with patch("bottle.request", self.request):
                with patch("ldap.initialize", return_value=self.ldap_server):
                    self.assertEqual(dict(ok=True), auth.login(self.database))
        cookie = str(bottle.response._cookies)  # pylint: disable=protected-access
        self.assertTrue(cookie.startswith("Set-Cookie: session_id="))
        self.assertFalse("domain=" in cookie.lower())

    def test_failed_login(self):
        """Test failed login."""
        self.ldap_server.simple_bind_s.side_effect = ldap.INVALID_CREDENTIALS  # pylint: disable=no-member
        with patch("logging.warning", Mock()):
            with patch("bottle.request", self.request):
                with patch("ldap.initialize", return_value=self.ldap_server):
                    self.assertEqual(dict(ok=False), auth.login(self.database))


class LogoutTests(unittest.TestCase):
    """Unit tests for the logout route."""
    def test_logout(self):
        """Test successful logout."""
        database = Mock()
        self.assertEqual(dict(ok=True), auth.logout(database))
