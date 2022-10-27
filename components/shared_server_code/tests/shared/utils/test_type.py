"""Unit tests for the type module."""

import unittest
from shared.utils.type import User


class UserTests(unittest.TestCase):
    """Unit tests user dataclass."""

    def setUp(self):
        """Override to set up test fixtures."""
        self.user = User(
            username="jadoe", email="jadoe@example.org", common_name="Jane Doe", settings={"test_setting": True}
        )

    def test_to_dict(self):
        """Test that user converts into dict."""
        user_dict = self.user.to_dict()
        self.assertDictEqual(
            user_dict,
            dict(username="jadoe", email="jadoe@example.org", common_name="Jane Doe", settings={"test_setting": True}),
        )

    def test_user_and_email(self):
        """Test that the user and email can be retrieved."""
        self.assertEqual("Jane Doe <jadoe@example.org>", self.user.name_and_email())
