"""Collectors for SonarQube."""

from typing import Dict, List

from dateutil.parser import isoparse
import requests

from utilities.type import URL, Entities, Entity, Value
from utilities.functions import days_ago
from .source_collector import SourceCollector


class SonarQubeViolations(SourceCollector):
    """SonarQube violations metric. Also base class for metrics that measure specific rules."""

    rules_parameter = "Subclass responsibility"

    def _landing_url(self, responses: List[requests.Response]) -> URL:
        url = super()._landing_url(responses)
        component = self._parameter("component")
        landing_url = f"{url}/project/issues?id={component}&resolved=false"
        return URL(landing_url + self.__rules_url_parameter())

    def _api_url(self) -> URL:
        url = super()._api_url()
        component = self._parameter("component")
        severities = ",".join([severity.upper() for severity in self._parameter("severities")])
        types = ",".join([violation_type.upper() for violation_type in self._parameter("types")])
        # If there's more than 500 issues only the first 500 are returned. This is no problem since we limit
        # the number of "entities" sent to the server anyway (that limit is 100 currently).
        api = f"{url}/api/issues/search?componentKeys={component}&resolved=false&ps=500&" \
              f"severities={severities}&types={types}"
        return URL(api + self.__rules_url_parameter())

    def __rules_url_parameter(self) -> str:
        """Return the rules url parameter, if any."""
        rules = self._parameter(self.rules_parameter) if self.rules_parameter != "Subclass responsibility" else []
        return f"&rules={','.join(rules)}" if rules else ""

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(sum(int(response.json()["total"]) for response in responses))

    def _parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        return [self._entity(issue, response) for response in responses for issue in response.json()["issues"]]

    def __issue_landing_url(self, issue_key: str, response: requests.Response) -> URL:
        """Generate a landing url for the issue."""
        url = super()._landing_url([response])
        component = self._parameter("component")
        return URL(f"{url}/project/issues?id={component}&issues={issue_key}&open={issue_key}")

    def _entity(self, issue, response: requests.Response) -> Entity:
        """Create an entity from an issue."""
        return dict(
            key=issue["key"],
            url=self.__issue_landing_url(issue["key"], response),
            message=issue["message"],
            severity=issue["severity"].lower(),
            type=issue["type"].lower(),
            component=issue["component"])


class SonarQubeCommentedOutCode(SonarQubeViolations):
    """SonarQube commented out code collector."""

    rules_parameter = "commented_out_rules"


class SonarQubeComplexUnits(SonarQubeViolations):
    """SonarQube long methods collector."""

    rules_parameter = "complex_unit_rules"


class SonarQubeLongUnits(SonarQubeViolations):
    """SonarQube long methods collector."""

    rules_parameter = "long_unit_rules"


class SonarQubeManyParameters(SonarQubeViolations):
    """SonarQube many parameters collector."""

    rules_parameter = "many_parameter_rules"


class SonarQubeSuppressedViolations(SonarQubeViolations):
    """SonarQube suppressed violations collector."""

    rules_parameter = "suppression_rules"

    def _get_source_responses(self, api_url: URL) -> List[requests.Response]:
        """Next to the suppressed rules, also get issues closed as false positive and won't fix from SonarQube."""
        responses = super()._get_source_responses(api_url)
        url = SourceCollector._api_url(self)  # pylint: disable=protected-access
        component = self._parameter("component")
        api_url = URL(f"{url}/api/issues/search?componentKeys={component}&status=RESOLVED&"
                      "resolutions=WONTFIX,FALSE-POSITIVE&ps=500")
        return responses + [requests.get(api_url, timeout=self.TIMEOUT, auth=self._basic_auth_credentials())]

    def _entity(self, issue, response: requests.Response) -> Entity:
        """Also add the resolution to the entity."""
        entity = super()._entity(issue, response)
        resolution = issue.get("resolution", "").lower()
        entity["resolution"] = dict(wontfix="won't fix").get(resolution, resolution)
        return entity


class SonarQubeMetricsBaseClass(SourceCollector):
    """Base class for collectors that use the SonarQube measures/component API."""

    # Metric keys is a string containing one or two metric keys separated by a comma. The first metric key is used for
    # the metric value, the second for the total value (used for calculating a percentage).
    metricKeys = "Subclass responsibility"

    def _landing_url(self, responses: List[requests.Response]) -> URL:
        url = super()._landing_url(responses)
        component = self._parameter("component")
        return URL(f"{url}/component_measures?id={component}&metric={self.metricKeys}")

    def _api_url(self) -> URL:
        url = super()._api_url()
        component = self._parameter("component")
        return URL(f"{url}/api/measures/component?component={component}&metricKeys={self.metricKeys}")

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(self.__get_metrics(responses)[self.metricKeys.split(",")[0]])

    def _parse_source_responses_total(self, responses: List[requests.Response]) -> Value:
        return str(self.__get_metrics(responses)[self.metricKeys.split(",")[1]])

    @staticmethod
    def __get_metrics(responses: List[requests.Response]) -> Dict[str, int]:
        """Get the metric(s) from the responses."""
        measures = [measure for measure in responses[0].json()["component"]["measures"]]
        return dict((measure["metric"], int(measure["value"])) for measure in measures)


class SonarQubeDuplicatedLines(SonarQubeMetricsBaseClass):
    """SonarQube duplicated lines collector."""

    metricKeys = "duplicated_lines,lines"


class SonarQubeTests(SonarQubeMetricsBaseClass):
    """SonarQube tests collector."""

    metricKeys = "tests"


class SonarQubeFailedTests(SonarQubeMetricsBaseClass):
    """SonarQube failed tests collector."""

    metricKeys = "test_failures"


class SonarQubeNCLOC(SonarQubeMetricsBaseClass):
    """SonarQube non-commented lines of code."""

    metricKeys = "ncloc"


class SonarQubeLOC(SonarQubeMetricsBaseClass):
    """SonarQube lines of code."""

    metricKeys = "lines"


class SonarQubeUncoveredLines(SonarQubeMetricsBaseClass):
    """SonarQube uncovered lines of code."""

    metricKeys = "uncovered_lines,lines_to_cover"


class SonarQubeUncoveredBranches(SonarQubeMetricsBaseClass):
    """SonarQube uncovered branches."""

    metricKeys = "uncovered_conditions,conditions_to_cover"


class SonarQubeSourceUpToDateness(SourceCollector):
    """SonarQube source up-to-dateness."""

    def _api_url(self) -> URL:
        url = super()._api_url()
        return URL(f"{url}/api/project_analyses/search?project={self._parameter('component')}")

    def _landing_url(self, responses: List[requests.Response]) -> URL:
        url = super()._landing_url(responses)
        return URL(f"{url}/project/activity?id={self._parameter('component')}")

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        analysis_datetime = isoparse(responses[0].json()["analyses"][0]["date"])
        return str(days_ago(analysis_datetime))
