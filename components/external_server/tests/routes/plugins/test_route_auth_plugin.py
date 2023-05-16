"""Unit tests for the route authentication plugin."""

import logging
from datetime import datetime, timezone

import bottle

from shared.routes.plugins import InjectionPlugin
from shared.utils.type import User

from routes.plugins.auth_plugin import AuthPlugin, EDIT_REPORT_PERMISSION

from ...base import DatabaseTestCase


class AuthPluginTest(DatabaseTestCase):
    """Unit tests for the route authentication and authorization plugin."""

    def setUp(self):
        """Override to set up a mock database and install the plugins."""
        super().setUp()
        logging.disable(logging.CRITICAL)
        self.database.reports_overviews.find_one.return_value = dict(_id="id")
        self.database.sessions.find_one.return_value = None
        self.session = dict(
            user="jadoe",
            email="jadoe@example.org",
            session_expiration_datetime=datetime.max.replace(tzinfo=timezone.utc),
        )
        self.injection_plugin = bottle.install(InjectionPlugin(self.database, "database"))
        self.auth_plugin = bottle.install(AuthPlugin())

    def tearDown(self):
        """Override to remove the plugins and reset the logging."""
        bottle.uninstall(self.auth_plugin)
        bottle.uninstall(self.injection_plugin)
        logging.disable(logging.NOTSET)

    @staticmethod
    def route(database, user: User = None):
        """Route handler with injected parameters. Returns the parameters for test purposes."""
        return database, user

    def test_route_without_specified_auth(self):
        """Test that the auth plugin will crash."""
        route = bottle.Route(bottle.app(), "/", "POST", self.route)
        with self.assertRaises(AttributeError):
            route.call()

    def test_valid_session(self):
        """Test that session ids are authenticated."""
        self.database.sessions.find_one.return_value = dict(
            session_expiration_datetime=datetime.max.replace(tzinfo=timezone.utc)
        )
        route = bottle.Route(bottle.app(), "/", "POST", self.route, authentication_required=True)
        self.assertEqual((self.database, None), route.call())

    def test_expired_session(self):
        """Test that the session is invalid when it's expired."""
        self.database.sessions.find_one.return_value = dict(
            session_expiration_datetime=datetime.min.replace(tzinfo=timezone.utc)
        )
        route = bottle.Route(bottle.app(), "/", "POST", self.route, authentication_required=True)
        self.assertEqual(401, route.call().status_code)

    def test_missing_session(self):
        """Test that the session is invalid when it's missing."""
        route = bottle.Route(bottle.app(), "/", "POST", self.route, authentication_required=True)
        self.assertEqual(401, route.call().status_code)

    def test_unauthorized_session(self):
        """Test that an unauthorized user cannot post."""
        self.database.reports_overviews.find_one.return_value = dict(
            _id="id", permissions={EDIT_REPORT_PERMISSION: ["jodoe"]}
        )
        self.database.sessions.find_one.return_value = self.session
        route = bottle.Route(bottle.app(), "/", "POST", self.route, permissions_required=[EDIT_REPORT_PERMISSION])
        self.assertEqual(403, route.call().status_code)

    def test_post_route_with_permissions_required_when_everyone_has_permission(self):
        """Test that an authenticated user can post if permissions have not been restricted."""
        self.database.reports_overviews.find_one.return_value = dict(_id="id", permissions={})
        self.database.sessions.find_one.return_value = self.session
        route = bottle.Route(bottle.app(), "/", "POST", self.route, permissions_required=[EDIT_REPORT_PERMISSION])
        self.assertEqual((self.database, None), route.call())

    def test_post_route_with_permissions_required(self):
        """Test that an authenticated user can post if they have the required permissions."""
        self.database.reports_overviews.find_one.return_value = dict(
            _id="id", permissions={EDIT_REPORT_PERMISSION: ["jadoe"]}
        )
        self.database.sessions.find_one.return_value = self.session
        route = bottle.Route(bottle.app(), "/", "POST", self.route, permissions_required=[EDIT_REPORT_PERMISSION])
        self.assertEqual((self.database, None), route.call())

    def test_post_route_without_authentication_required(self):
        """Test that unauthenticated users can POST if no authentication is required."""
        route = bottle.Route(bottle.app(), "/", "POST", self.route, authentication_required=False)
        self.assertEqual((self.database, None), route.call())

    def test_get_route_without_authentication_required(self):
        """Test that unauthenticated users can GET if no authentication is required."""
        route = bottle.Route(bottle.app(), "/", "GET", self.route, authentication_required=False)
        self.assertEqual((self.database, None), route.call())

    def test_pass_user(self):
        """Test that the user can be passed to the route."""
        self.database.sessions.find_one.return_value = dict(
            session_expiration_datetime=datetime.max.replace(tzinfo=timezone.utc), user="user"
        )
        route = bottle.Route(bottle.app(), "/", "POST", self.route, authentication_required=True, pass_user=True)
        self.assertEqual((self.database, User("user")), route.call())
