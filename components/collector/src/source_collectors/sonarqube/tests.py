"""SonarQube tests collector."""

from collector_utilities.type import URL
from model import SourceMeasurement, SourceResponses

from .base import SonarQubeCollector


class SonarQubeTests(SonarQubeCollector):
    """SonarQube collector for the tests metric."""

    async def _api_url(self) -> URL:
        """Extend to add the measures path and parameters."""
        url = await super()._api_url()
        component = self._parameter("component")
        branch = self._parameter("branch")
        metric_keys = "tests,test_errors,test_failures,skipped_tests"
        return URL(f"{url}/api/measures/component?component={component}&metricKeys={metric_keys}&branch={branch}")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the measures path and parameters."""
        url = await super()._landing_url(responses)
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(f"{url}/component_measures?id={component}&metric=tests&branch={branch}")

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the number of tests."""
        tests = await self.__nr_of_tests(responses)
        value = str(sum(tests[test_result] for test_result in self._parameter("test_result")))
        test_results = self._data_model["sources"][self.source_type]["parameters"]["test_result"]["values"]
        total = str(sum(tests[test_result] for test_result in test_results))
        return SourceMeasurement(value=value, total=total)

    @staticmethod
    async def __nr_of_tests(responses: SourceResponses) -> dict[str, int]:
        """Return the number of tests by test result."""
        measures = {
            measure["metric"]: int(measure["value"]) for measure in (await responses[0].json())["component"]["measures"]
        }
        errored = measures.get("test_errors", 0)
        failed = measures.get("test_failures", 0)
        skipped = measures.get("skipped_tests", 0)
        passed = measures["tests"] - errored - failed - skipped  # Throw an exception (KeyError) if there are no tests
        return dict(errored=errored, failed=failed, skipped=skipped, passed=passed)
