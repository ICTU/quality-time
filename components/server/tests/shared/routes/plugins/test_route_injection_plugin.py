"""Unit tests for the route injection plugin model."""

import unittest

import bottle

from external.routes.plugins import AuthPlugin
from shared.routes.plugins import InjectionPlugin


class RouteInjectionPluginTest(unittest.TestCase):
    """Unit tests for the route injection plugin."""

    def tearDown(self):
        """Override to remove the plugins."""
        bottle.app().uninstall(True)

    def test_install_plugin(self):
        """Test that setup raises an error when the same keyword is used by another plugin."""
        bottle.install(AuthPlugin())  # Totally different plugin, should be ignored
        plugin = InjectionPlugin("value", "keyword1")
        bottle.install(plugin)
        plugin_with_different_keyword = InjectionPlugin("value", "keyword2")
        bottle.install(plugin_with_different_keyword)
        plugin_with_same_keyword = InjectionPlugin("value", "keyword1")
        self.assertRaises(RuntimeError, bottle.install, plugin_with_same_keyword)

    def test_apply_plugin(self):
        """Test that the plugin can be applied to a route."""

        def route(keyword):
            """Fake route."""
            return keyword

        bottle.install(InjectionPlugin("value", "keyword"))
        route = bottle.Route(bottle.app(), "/", "GET", route)
        self.assertEqual("value", route.call())

    def test_apply_plugin_to_route_that_does_not_take_keyword(self):
        """Test that the plugin can be applied to a route."""

        def route():
            """Fake route."""
            return "route"

        bottle.install(InjectionPlugin("value", "keyword"))
        route = bottle.Route(bottle.app(), "/", "GET", route)
        self.assertEqual("route", route.call())
