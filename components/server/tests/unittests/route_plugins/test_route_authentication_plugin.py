"""Unit tests for the route authentication plugin."""

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

    def test_apply_valid_session(self):
        """Test that session ids are authenticated."""
        bottle.install(InjectionPlugin(Mock(), "database"))
        bottle.install(AuthenticationPlugin())
        route = bottle.Route(bottle.app(), "/", "POST", self.route)
        self.assertEqual("route called", route.call())

    def test_apply_invalid_session(self):
        """Test that session ids are authenticated."""
        database_mock = Mock()
        database_mock.sessions.find_one.return_value = None
        bottle.install(InjectionPlugin(database_mock, "database"))
        bottle.install(AuthenticationPlugin())
        route = bottle.Route(bottle.app(), "/", "POST", self.route)
        with patch("logging.warning", Mock()):  # Suppress logging
            self.assertEqual(dict(ok=False), route.call())

    def test_apply_to_get_route(self):
        """Test that session ids are not authenticated with non-post routes."""
        database_mock = Mock()
        database_mock.sessions.find_one.return_value = None
        bottle.install(InjectionPlugin(database_mock, "database"))
        bottle.install(AuthenticationPlugin())
        route = bottle.Route(bottle.app(), "/", "GET", self.route)
        self.assertEqual("route called", route.call())
