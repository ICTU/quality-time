import unittest

import requests


class ApiTest(unittest.TestCase):
    def test_documentation(self):
        """Test that the documentation API is available."""
        apis = requests.get("http://www:80/api").json().keys()
        self.assertTrue("/api/v1/login" in apis)
        self.assertTrue("/api/v2/login" in apis)
