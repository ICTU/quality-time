"""Unit tests for the type module."""

import unittest
from shared.utils.type import User


class UserTests(unittest.TestCase):
    """Unit tests user dataclass."""

    def test_to_dict(self):
        """Test that user convers into dict."""
        user = User(username="jadoe", email="jadoe@qt.com", common_name="Jane Doe", settings={"test_setting": True})
        user_dict = user.to_dict()

        self.assertDictEqual(
            user_dict,
            dict(username="jadoe", email="jadoe@qt.com", common_name="Jane Doe", settings={"test_setting": True}),
        )
