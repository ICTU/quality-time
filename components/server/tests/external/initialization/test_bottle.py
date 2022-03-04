"""Unit tests for the bottle initialization."""

import unittest
from unittest.mock import Mock
import bottle

from shared.routes.plugins import InjectionPlugin

from external.routes.plugins import AuthPlugin
from external.initialization import init_bottle


class BottleInitTest(unittest.TestCase):
    """Unit tests for the bottle initialization."""

    def tearDown(self):
        """Override to remove the plugins."""
        bottle.uninstall(AuthPlugin)
        bottle.uninstall(InjectionPlugin)

    def test_init(self):
        """Test that bottle has been initialized."""
        init_bottle(Mock())
        self.assertEqual(1024 * 1024, bottle.BaseRequest.MEMFILE_MAX)
        self.assertEqual([InjectionPlugin, AuthPlugin], [plugin.__class__ for plugin in bottle.app().plugins[-2:]])
