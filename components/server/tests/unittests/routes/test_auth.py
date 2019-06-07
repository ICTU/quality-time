"""Unit tests for the authorization routes."""

import unittest
from unittest import mock

import ldap  # pylint: disable=import-error

from src.routes import auth


class LoginTests(unittest.TestCase):
    """Unit tests for the login route."""
    def test_successful_login(self):
        """Test successful login."""
        request = mock.Mock()
        request.json = dict(username="user", password="pass")
        database = mock.Mock()
        ldap_server = mock.Mock()
        with mock.patch("bottle.request", request):
            self.assertEqual(dict(ok=True), auth.login(database, ldap_server))

    def test_failed_login(self):
        """Test failed login."""
        request = mock.Mock()
        request.json = dict(username="user", password="pass")
        database = mock.Mock()
        ldap_server = mock.Mock()
        ldap_server.simple_bind_s = mock.Mock(side_effect=ldap.INVALID_CREDENTIALS)
        with mock.patch("logging.warning", mock.Mock()):
            with mock.patch("bottle.request", request):
                self.assertEqual(dict(ok=False), auth.login(database, ldap_server))


class LogoutTests(unittest.TestCase):
    """Unit tests for the logout route."""
    def test_logout(self):
        """Test successful logout."""
        database = mock.Mock()
        self.assertEqual(dict(ok=True), auth.logout(database))
