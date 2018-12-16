"""Unit tests for the API class."""

import unittest

from quality_time import api


class APITest(unittest.TestCase):
    """Unit tests for the API class."""

    def test_error_message(self):
        """Test the error message that is returned when no subclass has been registered."""
        handler = api.API.subclass_for_api("unknown_api")(dict())
        self.assertEqual(dict(request_error="Unknown <metric>/<source>"), handler.get(dict()))

    def test_subclass_registration(self):
        """Test that a subclass to handle a specific API can be found."""

        class RegisteredAPI(api.API):  # pylint: disable=unused-variable
            """Subclass for registered_api."""
            def get(self, *args, **kwargs):
                """Return the response."""
                return dict(result="Success")

        handler = api.API.subclass_for_api("registered_api")(dict())
        self.assertEqual(dict(result="Success"), handler.get(dict()))
