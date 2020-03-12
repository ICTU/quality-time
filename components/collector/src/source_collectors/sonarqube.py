"""Collectors for SonarQube."""

from datetime import datetime
from typing import Dict, List, Tuple

from dateutil.parser import isoparse

from collector_utilities.type import URL, Entities, Entity, Response, Responses, Value
from .source_collector import SourceCollector, SourceUpToDatenessCollector


class SonarQubeException(Exception):
    """Something went wrong collecting information from SonarQube."""


class SonarQubeCollector(SourceCollector):
    """Base class for SonarQube collectors."""

    async def _get_source_responses(self, api_url: URL) -> Responses:
        # SonarQube sometimes gives results (e.g. zero violations) even if the component does not exist, so we
        # check whether the component specified by the user actually exists before getting the data.
        url = await SourceCollector._api_url(self)
        component = self._parameter("component")
        show_component_url = URL(f"{url}/api/components/show?component={component}")
        response = (await super()._get_source_responses(show_component_url))[0]
        json = await response.json()
        if "errors" in json:
            raise SonarQubeException(json["errors"][0]["msg"])
        return await super()._get_source_responses(api_url)


class SonarQubeViolations(SonarQubeCollector):
    """SonarQube violations metric. Also base class for metrics that measure specific rules."""

    rules_parameter = ""  # Subclass responsibility

    async def _landing_url(self, responses: Responses) -> URL:
        url = await super()._landing_url(responses)
        component = self._parameter("component")
        branch = self._parameter("branch")
        landing_url = f"{url}/project/issues?id={component}&resolved=false&branch={branch}"
        return URL(landing_url + self.__rules_url_parameter())

    async def _api_url(self) -> URL:
        url = await super()._api_url()
        component = self._parameter("component")
        branch = self._parameter("branch")
        severities = ",".join([severity.upper() for severity in self._parameter("severities")])
        types = ",".join([violation_type.upper() for violation_type in self._parameter("types")])
        # If there's more than 500 issues only the first 500 are returned. This is no problem since we limit
        # the number of "entities" sent to the server anyway (that limit is 100 currently).
        api = f"{url}/api/issues/search?componentKeys={component}&resolved=false&ps=500&" \
              f"severities={severities}&types={types}&branch={branch}"
        return URL(api + self.__rules_url_parameter())

    def __rules_url_parameter(self) -> str:
        """Return the rules url parameter, if any."""
        rules = self._parameter(self.rules_parameter) if self.rules_parameter else []
        return f"&rules={','.join(rules)}" if rules else ""

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        value = 0
        entities: Entities = []
        for response in responses:
            json = await response.json()
            value += int(json.get("total", 0))
            entities.extend([await self._entity(issue) for issue in json.get("issues", [])])
        return str(value), "100", entities

    async def __issue_landing_url(self, issue_key: str) -> URL:
        """Generate a landing url for the issue."""
        url = await super()._landing_url([])
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(f"{url}/project/issues?id={component}&issues={issue_key}&open={issue_key}&branch={branch}")

    async def _entity(self, issue) -> Entity:
        """Create an entity from an issue."""
        return dict(
            key=issue["key"],
            url=await self.__issue_landing_url(issue["key"]),
            message=issue["message"],
            severity=issue["severity"].lower(),
            type=issue["type"].lower(),
            component=issue["component"])


class SonarQubeCommentedOutCode(SonarQubeViolations):
    """SonarQube commented out code collector."""

    # Unfortunately, the SonarQube API for commented out code doesn't seem to return the number of lines commented out,
    # so we can't compute a percentage of commented out code. And hence this collector is not a subclass of
    # SonarQubeViolationsWithPercentageScale.

    rules_parameter = "commented_out_rules"


class SonarQubeViolationsWithPercentageScale(SonarQubeViolations):
    """SonarQube violations collectors that support the percentage scale."""

    total_metric = ""  # Subclass responsibility

    async def _get_source_responses(self, api_url: URL) -> Responses:
        """Next to the violations, also get the total number of units as basis for the percentage scale."""
        responses = await super()._get_source_responses(api_url)
        component = self._parameter("component")
        branch = self._parameter("branch")
        base_api_url = await SonarQubeCollector._api_url(self)  # pylint: disable=protected-access
        total_metric_api_url = URL(
            f"{base_api_url}/api/measures/component?component={component}&metricKeys={self.total_metric}&"
            f"branch={branch}")
        return responses + await super()._get_source_responses(total_metric_api_url)

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        value, _, entities = await super()._parse_source_responses(responses)
        measures: List[Dict[str, str]] = []
        for response in responses:
            measures.extend((await response.json()).get("component", {}).get("measures", []))
        return value, str(sum(int(measure["value"]) for measure in measures)), entities


class SonarQubeComplexUnits(SonarQubeViolationsWithPercentageScale):
    """SonarQube complex methods/functions collector."""

    rules_parameter = "complex_unit_rules"
    total_metric = "functions"


class SonarQubeLongUnits(SonarQubeViolationsWithPercentageScale):
    """SonarQube long methods/functions collector."""

    rules_parameter = "long_unit_rules"
    total_metric = "functions"


class SonarQubeManyParameters(SonarQubeViolationsWithPercentageScale):
    """SonarQube many parameters collector."""

    rules_parameter = "many_parameter_rules"
    total_metric = "functions"


class SonarQubeSuppressedViolations(SonarQubeViolations):
    """SonarQube suppressed violations collector."""

    rules_parameter = "suppression_rules"

    async def _get_source_responses(self, api_url: URL) -> Responses:
        """In addition to the suppressed rules, also get issues closed as false positive and won't fix from SonarQube
        as well as the total number of violations."""
        responses = await super()._get_source_responses(api_url)
        url = await SourceCollector._api_url(self)  # pylint: disable=protected-access
        component = self._parameter("component")
        branch = self._parameter("branch")
        all_issues_api_url = URL(f"{url}/api/issues/search?componentKeys={component}&branch={branch}")
        resolved_issues_api_url = URL(f"{all_issues_api_url}&status=RESOLVED&resolutions=WONTFIX,FALSE-POSITIVE&ps=500")
        return responses + await super()._get_source_responses(
            resolved_issues_api_url) + await super()._get_source_responses(all_issues_api_url)

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        value, _, entities = await super()._parse_source_responses(responses[:-1])
        return value, str((await responses[-1].json())["total"]), entities

    async def _entity(self, issue) -> Entity:
        """Also add the resolution to the entity."""
        entity = await super()._entity(issue)
        resolution = issue.get("resolution", "").lower()
        entity["resolution"] = dict(wontfix="won't fix").get(resolution, resolution)
        return entity


class SonarQubeMetricsBaseClass(SonarQubeCollector):
    """Base class for collectors that use the SonarQube measures/component API."""

    # Metric keys is a string containing one or two metric keys separated by a comma. The first metric key is used for
    # the metric value, the second for the total value (used for calculating a percentage).
    metricKeys = ""  # Subclass responsibility

    async def _landing_url(self, responses: Responses) -> URL:
        url = await super()._landing_url(responses)
        component = self._parameter("component")
        branch = self._parameter("branch")
        metric = self._metric_keys().split(",")[0]
        return URL(f"{url}/component_measures?id={component}&metric={metric}&branch={branch}")

    async def _api_url(self) -> URL:
        url = await super()._api_url()
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(
            f"{url}/api/measures/component?component={component}&metricKeys={self._metric_keys()}&branch={branch}")

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        metric_keys = self._metric_keys().split(",")
        metrics = await self.__get_metrics(responses)
        value = str(metrics[metric_keys[0]])
        total = str(metrics[metric_keys[1]]) if len(metric_keys) > 1 else "100"
        return value, total, []

    def _metric_keys(self) -> str:
        """Return the SonarQube metric keys to use."""
        return self.metricKeys

    @staticmethod
    async def __get_metrics(responses: Responses) -> Dict[str, int]:
        """Get the metric(s) from the responses."""
        measures = (await responses[0].json())["component"]["measures"]
        # Without the local variable, coverage.py thinks: "line xyz didn't return from function '__get_metrics',
        # because the return on line xyz wasn't executed"
        metrics = dict((measure["metric"], int(measure["value"])) for measure in measures)
        return metrics


class SonarQubeDuplicatedLines(SonarQubeMetricsBaseClass):
    """SonarQube duplicated lines collector."""

    metricKeys = "duplicated_lines,lines"


class SonarQubeLOC(SonarQubeMetricsBaseClass):
    """SonarQube lines of code."""

    def _metric_keys(self) -> str:
        return str(self._parameter("lines_to_count"))


class SonarQubeUncoveredLines(SonarQubeMetricsBaseClass):
    """SonarQube uncovered lines of code."""

    metricKeys = "uncovered_lines,lines_to_cover"


class SonarQubeUncoveredBranches(SonarQubeMetricsBaseClass):
    """SonarQube uncovered branches."""

    metricKeys = "uncovered_conditions,conditions_to_cover"


class SonarQubeTests(SonarQubeCollector):
    """SonarQube collector for the tests metric."""

    async def _api_url(self) -> URL:
        url = await super()._api_url()
        component = self._parameter("component")
        branch = self._parameter("branch")
        metric_keys = "tests,test_errors,test_failures,skipped_tests"
        return URL(f"{url}/api/measures/component?component={component}&metricKeys={metric_keys}&branch={branch}")

    async def _landing_url(self, responses: Responses) -> URL:
        url = await super()._landing_url(responses)
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(f"{url}/component_measures?id={component}&metric=tests&branch={branch}")

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        tests = await self.__nr_of_tests(responses)
        value = str(sum(tests[test_result] for test_result in self._parameter("test_result")))
        test_results = self._datamodel["sources"][self.source_type]["parameters"]["test_result"]["values"]
        total = str(sum(tests[test_result] for test_result in test_results))
        return value, total, []

    @staticmethod
    async def __nr_of_tests(responses: Responses) -> Dict[str, int]:
        """Return the number of tests by test result."""
        measures = dict(
            (measure["metric"], int(measure["value"]))
            for measure in (await responses[0].json())["component"]["measures"])
        errored = measures.get("test_errors", 0)
        failed = measures.get("test_failures", 0)
        skipped = measures.get("skipped_tests", 0)
        passed = measures["tests"] - errored - failed - skipped  # Throw an exception (KeyError) if there are no tests
        return dict(errored=errored, failed=failed, skipped=skipped, passed=passed)


class SonarQubeSourceUpToDateness(SonarQubeCollector, SourceUpToDatenessCollector):
    """SonarQube source up-to-dateness."""

    async def _api_url(self) -> URL:
        url = await super()._api_url()
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(f"{url}/api/project_analyses/search?project={component}&branch={branch}")

    async def _landing_url(self, responses: Responses) -> URL:
        url = await super()._landing_url(responses)
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(f"{url}/project/activity?id={component}&branch={branch}")

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        return isoparse((await response.json())["analyses"][0]["date"])
