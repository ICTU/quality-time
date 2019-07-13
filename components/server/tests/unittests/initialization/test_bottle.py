"""Unit tests for the bottle initialization."""

import unittest
from unittest.mock import Mock

import bottle

from src.initialization.bottle import init_bottle
from src.route_plugins import AuthenticationPlugin, InjectionPlugin


class BottleInitTest(unittest.TestCase):
    """Unit tests for the bottle initialization."""

    def tearDown(self):
        bottle.app().uninstall(True)

    def test_init(self):
        """Test that bottle has been initialized."""
        init_bottle(Mock())
        self.assertEqual(1024 * 1024, bottle.BaseRequest.MEMFILE_MAX)
        self.assertEqual(
            [InjectionPlugin, AuthenticationPlugin], [plugin.__class__ for plugin in bottle.app().plugins[-2:]])
