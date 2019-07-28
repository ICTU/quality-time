"""Unit tests for the route authentication plugin."""

from datetime import datetime
import unittest
from unittest.mock import Mock, patch

import bottle

from routes.plugins import AuthenticationPlugin, InjectionPlugin


class AuthenticationPluginTest(unittest.TestCase):
    """Unit tests for the route authentication plugin."""

    def tearDown(self):
        bottle.app().uninstall(True)

    @staticmethod
    def route(database):  # pylint: disable=unused-argument
        """Route handler with database parameter."""
        return "route called"

    def test_valid_session(self):
        """Test that session ids are authenticated."""
        mock_database = Mock()
        mock_database.sessions.find_one.return_value = dict(session_expiration_datetime=datetime.max)
        bottle.install(InjectionPlugin(mock_database, "database"))
        bottle.install(AuthenticationPlugin())
        route = bottle.Route(bottle.app(), "/", "POST", self.route)
        self.assertEqual("route called", route.call())

    def test_expired_session(self):
        """Test that the session is invalid when it's experied."""
        mock_database = Mock()
        mock_database.sessions.find_one.return_value = dict(session_expiration_datetime=datetime.min)
        bottle.install(InjectionPlugin(mock_database, "database"))
        bottle.install(AuthenticationPlugin())
        route = bottle.Route(bottle.app(), "/", "POST", self.route)
        with patch("logging.warning", Mock()):  # Suppress logging
            self.assertEqual(dict(ok=False, reason="invalid_session"), route.call())

    def test_missing_session(self):
        """Test that the session is invalid when it's missing."""
        database_mock = Mock()
        database_mock.sessions.find_one.return_value = None
        bottle.install(InjectionPlugin(database_mock, "database"))
        bottle.install(AuthenticationPlugin())
        route = bottle.Route(bottle.app(), "/", "POST", self.route)
        with patch("logging.warning", Mock()):  # Suppress logging
            self.assertEqual(dict(ok=False, reason="invalid_session"), route.call())

    def test_http_get_routes(self):
        """Test that session ids are not authenticated with non-post routes."""
        database_mock = Mock()
        database_mock.sessions.find_one.return_value = None
        bottle.install(InjectionPlugin(database_mock, "database"))
        bottle.install(AuthenticationPlugin())
        route = bottle.Route(bottle.app(), "/", "GET", self.route)
        self.assertEqual("route called", route.call())
