"""LDAP initialization unit tests."""

import unittest
from unittest.mock import patch

import bottle

from src.initialization.ldap import init_ldap
from src.route_plugins import InjectionPlugin


class LDAPInitTest(unittest.TestCase):
    """Unit tests for the LDAP initialization function."""

    def tearDown(self):
        bottle.app().uninstall(True)

    @patch("ldap.initialize")
    def test_init(self, mock_ldap_init):
        """Test that the LDAP connection is initialized and injected to the routes."""
        init_ldap()
        mock_ldap_init.assert_called_once()
        self.assertEqual(InjectionPlugin, bottle.app().plugins[-1].__class__)
