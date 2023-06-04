"""Unit tests for the SonarQube LOC collector."""

from .base import SonarQubeTestCase


class SonarQubeLOCTest(SonarQubeTestCase):
    """Unit tests for the SonarQube LOC collector."""

    METRIC_TYPE = "loc"

    async def test_loc_returns_ncloc_by_default(self):
        """Test that the number of lines of non-comment code is returned."""
        json = {
            "component": {
                "measures": [
                    {"metric": "ncloc", "value": "1234"},
                    {"metric": "ncloc_language_distribution", "value": "py=1000;js=234"},
                ],
            },
        }
        response = await self.collect(get_request_json_return_value=json)
        self.assert_measurement(
            response,
            value="1234",
            total="100",
            entities=[
                {"key": "py", "language": "Python", "ncloc": "1000"},
                {"key": "js", "language": "JavaScript", "ncloc": "234"},
            ],
            landing_url=self.metric_landing_url.format("ncloc"),
        )

    async def test_loc_all_lines(self):
        """Test that the number of lines of code is returned."""
        self.set_source_parameter("lines_to_count", "all lines")
        json = {
            "component": {
                "measures": [
                    {"metric": "lines", "value": "1234"},
                    {"metric": "ncloc_language_distribution", "value": "py=999;js=10"},
                ],
            },
        }
        response = await self.collect(get_request_json_return_value=json)
        self.assert_measurement(
            response,
            value="1234",
            total="100",
            entities=[],
            landing_url=self.metric_landing_url.format("lines"),
        )

    async def test_loc_ignore_languages(self):
        """Test that languages can be ignored."""
        self.set_source_parameter("languages_to_ignore", ["JavaScript"])
        json = {
            "component": {
                "measures": [
                    {"metric": "ncloc", "value": "1500"},
                    {"metric": "ncloc_language_distribution", "value": "py=1000;js=500"},
                ],
            },
        }
        response = await self.collect(get_request_json_return_value=json)
        self.assert_measurement(
            response,
            value="1000",
            total="100",
            entities=[{"key": "py", "language": "Python", "ncloc": "1000"}],
            landing_url=self.metric_landing_url.format("ncloc"),
        )
