"""Unit tests for the route authentication plugin."""

import logging
import unittest
from datetime import datetime, timezone
from unittest.mock import Mock

import bottle

from shared.routes.plugins import AuthPlugin, InjectionPlugin
from shared.routes.plugins.auth_plugin import EDIT_REPORT_PERMISSION


class AuthPluginTest(unittest.TestCase):
    """Unit tests for the route authentication and authorization plugin."""

    def setUp(self):
        """Override to set up a mock database and install the plugins."""
        logging.disable()
        self.database = Mock()
        self.database.reports_overviews.find_one.return_value = dict(_id="id")
        self.success = dict(ok=True)
        self.session = dict(
            user="jadoe",
            email="jadoe@example.org",
            session_expiration_datetime=datetime.max.replace(tzinfo=timezone.utc),
        )
        bottle.install(InjectionPlugin(self.database, "database"))
        bottle.install(AuthPlugin())

    def tearDown(self):
        """Override to remove the plugins and reset the logging."""
        bottle.app().uninstall(True)
        logging.disable(logging.NOTSET)

    def route(self, database):  # pylint: disable=unused-argument
        """Route handler with database parameter."""
        return self.success

    def test_route_without_specified_auth(self):
        """Test that the auth plugin will crash."""
        with self.assertRaises(AttributeError):
            route = bottle.Route(bottle.app(), "/", "POST", self.route)
            route.call()

    def test_valid_session(self):
        """Test that session ids are authenticated."""
        self.database.sessions.find_one.return_value = dict(
            session_expiration_datetime=datetime.max.replace(tzinfo=timezone.utc)
        )
        route = bottle.Route(bottle.app(), "/", "POST", self.route, authentication_required=True)
        self.assertEqual(self.success, route.call())

    def test_expired_session(self):
        """Test that the session is invalid when it's expired."""
        self.database.sessions.find_one.return_value = dict(
            session_expiration_datetime=datetime.min.replace(tzinfo=timezone.utc)
        )
        route = bottle.Route(bottle.app(), "/", "POST", self.route, authentication_required=True)
        self.assertRaises(bottle.HTTPError, route.call)

    def test_missing_session(self):
        """Test that the session is invalid when it's missing."""
        self.database.sessions.find_one.return_value = None
        route = bottle.Route(bottle.app(), "/", "POST", self.route, authentication_required=True)
        self.assertRaises(bottle.HTTPError, route.call)

    def test_unauthorized_session(self):
        """Test that an unauthorized user cannot post."""
        self.database.reports_overviews.find_one.return_value = dict(
            _id="id", permissions={EDIT_REPORT_PERMISSION: ["jodoe"]}
        )
        self.database.sessions.find_one.return_value = self.session
        route = bottle.Route(bottle.app(), "/", "POST", self.route, permissions_required=[EDIT_REPORT_PERMISSION])
        self.assertRaises(bottle.HTTPError, route.call)

    def test_no_authorized_users_means_everybody_is_authorized(self):
        """Test that an unauthorized user cannot post."""
        self.database.reports_overviews.find_one.return_value = dict(_id="id", permissions={})
        self.database.sessions.find_one.return_value = self.session
        route = bottle.Route(bottle.app(), "/", "POST", self.route, permissions_required=[EDIT_REPORT_PERMISSION])
        self.assertEqual(self.success, route.call())

    def test_authorized_session(self):
        """Test that an authorized user can post."""
        self.database.reports_overviews.find_one.return_value = dict(
            _id="id", permissions={EDIT_REPORT_PERMISSION: ["jadoe"]}
        )
        self.database.sessions.find_one.return_value = self.session
        route = bottle.Route(bottle.app(), "/", "POST", self.route, permissions_required=[EDIT_REPORT_PERMISSION])
        self.assertEqual(self.success, route.call())

    def test_non_protected_route(self):
        """Test that the session is invalid when it's missing."""
        self.database.sessions.find_one.return_value = None
        route = bottle.Route(bottle.app(), "/", "POST", self.route, authentication_required=False)
        self.assertEqual(self.success, route.call())

    def test_http_get_routes(self):
        """Test that session ids are not authenticated if no authentication is required."""
        self.database.sessions.find_one.return_value = None
        route = bottle.Route(bottle.app(), "/", "GET", self.route, authentication_required=False)
        self.assertEqual(self.success, route.call())
