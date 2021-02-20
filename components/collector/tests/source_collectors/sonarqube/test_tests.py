"""Unit tests for the SonarQube tests collector."""

from .base import SonarQubeTestCase


class SonarQubeTestsTest(SonarQubeTestCase):
    """Unit tests for the SonarQube tests collector."""

    METRIC_TYPE = "tests"

    def assert_measurement(self, measurement, *, source_index: int = 0, **attributes) -> None:
        """Extend to add the landing url."""
        attributes["landing_url"] = "https://sonarqube/component_measures?id=id&metric=tests&branch=master"
        super().assert_measurement(measurement, source_index=source_index, **attributes)

    async def test_nr_of_tests(self):
        """Test that the number of tests is returned."""
        json = dict(component=dict(measures=[dict(metric="tests", value="123")]))
        response = await self.collect(self.metric, get_request_json_return_value=json)
        self.assert_measurement(response, value="123", total="123")

    async def test_nr_of_skipped_tests(self):
        """Test that the number of skipped tests is returned."""
        json = dict(
            component=dict(measures=[dict(metric="tests", value="123"), dict(metric="skipped_tests", value="4")])
        )
        self.sources["source_id"]["parameters"]["test_result"] = ["skipped"]
        response = await self.collect(self.metric, get_request_json_return_value=json)
        self.assert_measurement(response, value="4", total="123")

    async def test_nr_of_tests_without_tests(self):
        """Test that the collector throws an exception if there are no tests."""
        json = dict(component=dict(measures=[]))
        response = await self.collect(self.metric, get_request_json_return_value=json)
        self.assert_measurement(response, value=None, total="100", parse_error="KeyError")

    async def test_nr_of_tests_with_faulty_component(self):
        """Test that the measurement fails if the component does not exist."""
        json = dict(errors=[dict(msg="No such component")])
        response = await self.collect(self.metric, get_request_json_return_value=json)
        self.assert_measurement(response, value=None, total=None, connection_error="No such component")
