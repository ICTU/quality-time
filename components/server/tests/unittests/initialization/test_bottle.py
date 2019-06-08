"""Unit tests for the bottle initialization."""

import unittest

import bottle

from src.initialization.bottle import init_bottle
from src.route_authentication_plugin import AuthenticationPlugin


class BottleInitTest(unittest.TestCase):
    """Unit tests for the bottle initialization."""

    def tearDown(self):
        bottle.app().uninstall(True)

    def test_init(self):
        """Test that bottle has been initialized."""
        init_bottle()
        self.assertEqual(1024 * 1024, bottle.BaseRequest.MEMFILE_MAX)
        self.assertEqual(AuthenticationPlugin, bottle.app().plugins[-1].__class__)
