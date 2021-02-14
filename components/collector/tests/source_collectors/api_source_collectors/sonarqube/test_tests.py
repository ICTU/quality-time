"""Unit tests for the SonarQube tests collector."""

from .base import SonarQubeTestCase


class SonarQubeTestsTest(SonarQubeTestCase):
    """Unit tests for the SonarQube tests collector."""

    def setUp(self):
        """Extend to set up the metric fixture."""
        super().setUp()
        self.metric = dict(type="tests", addition="sum", sources=self.sources)

    async def test_nr_of_tests(self):
        """Test that the number of tests is returned."""
        json = dict(component=dict(measures=[dict(metric="tests", value="123")]))
        response = await self.collect(self.metric, get_request_json_return_value=json)
        self.assert_measurement(response, value="123", total="123", landing_url=self.tests_landing_url)

    async def test_nr_of_skipped_tests(self):
        """Test that the number of skipped tests is returned."""
        json = dict(
            component=dict(measures=[dict(metric="tests", value="123"), dict(metric="skipped_tests", value="4")])
        )
        self.sources["source_id"]["parameters"]["test_result"] = ["skipped"]
        response = await self.collect(self.metric, get_request_json_return_value=json)
        self.assert_measurement(response, value="4", total="123", landing_url=self.tests_landing_url)

    async def test_nr_of_tests_without_tests(self):
        """Test that the collector throws an exception if there are no tests."""
        json = dict(component=dict(measures=[]))
        response = await self.collect(self.metric, get_request_json_return_value=json)
        self.assert_measurement(
            response, value=None, total=None, parse_error="KeyError", landing_url=self.tests_landing_url
        )

    async def test_nr_of_tests_with_faulty_component(self):
        """Test that the measurement fails if the component does not exist."""
        response = await self.collect(
            self.metric, get_request_json_return_value=dict(errors=[dict(msg="No such component")])
        )
        self.assert_measurement(
            response, value=None, total=None, connection_error="No such component", landing_url=self.tests_landing_url
        )
