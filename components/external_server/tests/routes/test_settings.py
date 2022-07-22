"""Unit tests for the settings routes."""

import unittest
from unittest.mock import Mock, patch
from routes.settings import find_user, get_settings, update_settings

USERNAME = "john-doe"
PASSWORD = "secret"


class SettingsTest(unittest.TestCase):  # skipcq: PTC-W0046
    """Test class for settings endpoints."""

    def setUp(self):
        """Override to set up a mock database."""
        self.database = Mock()
        self.database.users.find_one.return_value = {"username": "test", "settings": {"test_setting": True}}

    def test_find_user(self):
        """Test that a user can be found."""
        user = find_user(self.database)
        self.assertEqual(user.username, "test")
        self.assertDictEqual(user.settings, {"test_setting": True})

    def test_get_settings(self):
        """Retrieve the settings object."""
        settings_dict = get_settings(self.database)
        self.assertDictEqual(settings_dict, {"settings": {"test_setting": True}})

    @patch("bottle.request")
    def test_update_settings(self, request):
        """Update the settings object."""
        request.json = {"some_new_settings": False}
        response_dict = update_settings(
            self.database,
        )

        self.assertDictEqual(response_dict, dict(ok=True))
        self.database.users.replace_one.assert_called_once_with(
            {"username": "test"},
            {"username": "test", "email": "", "common_name": "", "settings": {"some_new_settings": False}},
            upsert=True,
        )
