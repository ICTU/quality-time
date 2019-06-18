"""Unit tests for the authorization routes."""

import unittest
from unittest.mock import Mock, patch

import ldap  # pylint: disable=import-error

from src.routes import auth


class LoginTests(unittest.TestCase):
    """Unit tests for the login route."""
    def test_successful_login(self):
        """Test successful login."""
        request = Mock()
        request.json = dict(username="user", password="pass")
        database = Mock()
        ldap_server = Mock()
        with patch("bottle.request", request):
            self.assertEqual(dict(ok=True), auth.login(database, ldap_server))

    def test_failed_login(self):
        """Test failed login."""
        request = Mock()
        request.json = dict(username="user", password="pass")
        database = Mock()
        ldap_server = Mock()
        ldap_server.simple_bind_s.side_effect = ldap.INVALID_CREDENTIALS
        with patch("logging.warning", Mock()):
            with patch("bottle.request", request):
                self.assertEqual(dict(ok=False), auth.login(database, ldap_server))


class LogoutTests(unittest.TestCase):
    """Unit tests for the logout route."""
    def test_logout(self):
        """Test successful logout."""
        database = Mock()
        self.assertEqual(dict(ok=True), auth.logout(database))
