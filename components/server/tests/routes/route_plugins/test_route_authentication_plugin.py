"""Unit tests for the route authentication plugin."""

import logging
import unittest
from datetime import datetime
from unittest.mock import Mock

import bottle

from routes.plugins import AuthenticationPlugin, InjectionPlugin


class AuthenticationPluginTest(unittest.TestCase):
    """Unit tests for the route authentication plugin."""

    def setUp(self):
        logging.disable()
        self.mock_database = Mock()
        self.success = dict(ok=True)
        bottle.install(InjectionPlugin(self.mock_database, "database"))
        bottle.install(AuthenticationPlugin())

    def tearDown(self):
        bottle.app().uninstall(True)
        logging.disable(logging.NOTSET)

    def route(self, database):  # pylint: disable=unused-argument
        """Route handler with database parameter."""
        return self.success

    def test_valid_session(self):
        """Test that session ids are authenticated."""
        self.mock_database.sessions.find_one.return_value = dict(session_expiration_datetime=datetime.max)
        route = bottle.Route(bottle.app(), "/", "POST", self.route)
        self.assertEqual(self.success, route.call())

    def test_expired_session(self):
        """Test that the session is invalid when it's expired."""
        self.mock_database.sessions.find_one.return_value = dict(session_expiration_datetime=datetime.min)
        route = bottle.Route(bottle.app(), "/", "POST", self.route)
        self.assertRaises(bottle.HTTPError, route.call)

    def test_missing_session(self):
        """Test that the session is invalid when it's missing."""
        self.mock_database.sessions.find_one.return_value = None
        route = bottle.Route(bottle.app(), "/", "POST", self.route)
        self.assertRaises(bottle.HTTPError, route.call)

    def test_http_get_routes(self):
        """Test that session ids are not authenticated with non-post routes."""
        self.mock_database.sessions.find_one.return_value = None
        route = bottle.Route(bottle.app(), "/", "GET", self.route)
        self.assertEqual(self.success, route.call())
