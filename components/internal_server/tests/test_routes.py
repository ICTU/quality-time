import os
import sys
import unittest
sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), 
                                               '../src/') ))

from fastapi.testclient import TestClient
from quality_time_server import internal_api

test_internal_api = TestClient(internal_api)

class TestInternalApi(unittest.TestCase):
    def test_get_health(self):
        response = test_internal_api.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_get_reports(self):
        response = test_internal_api.get("/api/reports")
        assert response.status_code == 200
        assert response.json() == []