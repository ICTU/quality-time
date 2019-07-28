"""Unit tests for the CORS module."""

import bottle
import unittest

from routes import cors


class CorsTest(unittest.TestCase):
    """Unit tests for the CORS handling."""

    def test_cors_generic_route(self):
        """Test that any request with an OPTIONS method will be handled."""
        route = bottle.app().match(dict(PATH_INFO="/", REQUEST_METHOD="options"))[0]
        self.assertEqual("", route.call())

    def test_enable_cors_after_request(self):
        """Test that CORS is enabled after every request."""
        cors.enable_cors_after_request_hook()
        self.assertEqual("http://localhost:3000", bottle.response.get_header("Access-Control-Allow-Origin"))
