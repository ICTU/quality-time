"""Collectors for SonarQube."""

from datetime import datetime
from typing import Dict, List

from dateutil.parser import isoparse

from base_collectors import SourceCollector, SourceCollectorException, SourceUpToDatenessCollector
from collector_utilities.functions import match_string_or_regular_expression
from collector_utilities.type import URL, Response
from source_model import Entity, SourceMeasurement, SourceResponses


class SonarQubeCollector(SourceCollector):
    """Base class for SonarQube collectors."""

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        # SonarQube sometimes gives results (e.g. zero violations) even if the component does not exist, so we
        # check whether the component specified by the user actually exists before getting the data.
        url = await SourceCollector._api_url(self)
        component = self._parameter("component")
        show_component_url = URL(f"{url}/api/components/show?component={component}")
        response = (await super()._get_source_responses(show_component_url))[0]
        json = await response.json()
        if "errors" in json:
            raise SourceCollectorException(json["errors"][0]["msg"])
        return await super()._get_source_responses(*urls)


class SonarQubeViolations(SonarQubeCollector):
    """SonarQube violations metric. Also base class for metrics that measure specific rules."""

    rules_configuration = ""  # Subclass responsibility
    types_parameter = "types"

    async def _landing_url(self, responses: SourceResponses) -> URL:
        url = await super()._landing_url(responses)
        component = self._parameter("component")
        branch = self._parameter("branch")
        landing_url = f"{url}/project/issues?id={component}&resolved=false&branch={branch}"
        return URL(landing_url + self.__rules_url_parameter())

    async def _api_url(self) -> URL:
        url = await super()._api_url()
        component = self._parameter("component")
        branch = self._parameter("branch")
        # If there's more than 500 issues only the first 500 are returned. This is no problem since we limit
        # the number of "entities" sent to the server anyway (that limit is 100 currently).
        api = (
            f"{url}/api/issues/search?componentKeys={component}&resolved=false&ps=500&"
            f"severities={self._violation_severities()}&types={self._violation_types()}&branch={branch}"
        )
        return URL(api + self.__rules_url_parameter())

    def __rules_url_parameter(self) -> str:
        """Return the rules url parameter, if any."""
        rules = (
            self._data_model["sources"][self.source_type]["configuration"][self.rules_configuration]["value"]
            if self.rules_configuration
            else []
        )
        return f"&rules={','.join(rules)}" if rules else ""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        value = 0
        entities: List[Entity] = []
        for response in responses:
            json = await response.json()
            value += int(json.get("total", 0))
            entities.extend([await self._entity(issue) for issue in json.get("issues", [])])
        return SourceMeasurement(value=str(value), entities=entities)

    async def __issue_landing_url(self, issue_key: str) -> URL:
        """Generate a landing url for the issue."""
        url = await super()._landing_url(SourceResponses())
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(f"{url}/project/issues?id={component}&issues={issue_key}&open={issue_key}&branch={branch}")

    async def _entity(self, issue) -> Entity:
        """Create an entity from an issue."""
        return Entity(
            key=issue["key"],
            url=await self.__issue_landing_url(issue["key"]),
            message=issue["message"],
            severity=issue.get("severity", "no severity").lower(),
            type=issue["type"].lower(),
            component=issue["component"],
            creation_date=issue["creationDate"],
            update_date=issue["updateDate"],
        )

    def _violation_types(self) -> str:
        """Return the violation types."""
        return ",".join(violation_type.upper() for violation_type in list(self._parameter(self.types_parameter)))

    def _violation_severities(self) -> str:
        """Return the severities parameter."""
        return ",".join(severity.upper() for severity in self._parameter("severities"))


class SonarQubeCommentedOutCode(SonarQubeViolations):
    """SonarQube commented out code collector."""

    # Unfortunately, the SonarQube API for commented out code doesn't seem to return the number of lines commented out,
    # so we can't compute a percentage of commented out code. And hence this collector is not a subclass of
    # SonarQubeViolationsWithPercentageScale.

    rules_configuration = "commented_out_rules"


class SonarQubeViolationsWithPercentageScale(SonarQubeViolations):
    """SonarQube violations collectors that support the percentage scale."""

    total_metric = ""  # Subclass responsibility

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Next to the violations, also get the total number of units as basis for the percentage scale."""
        component = self._parameter("component")
        branch = self._parameter("branch")
        base_api_url = await SonarQubeCollector._api_url(self)  # pylint: disable=protected-access
        total_metric_api_url = URL(
            f"{base_api_url}/api/measures/component?component={component}&metricKeys={self.total_metric}&"
            f"branch={branch}"
        )
        return await super()._get_source_responses(*(urls + (total_metric_api_url,)))

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        measurement = await super()._parse_source_responses(responses)
        measures: List[Dict[str, str]] = []
        for response in responses:
            measures.extend((await response.json()).get("component", {}).get("measures", []))
        measurement.total = str(sum(int(measure["value"]) for measure in measures))
        return measurement


class SonarQubeComplexUnits(SonarQubeViolationsWithPercentageScale):
    """SonarQube complex methods/functions collector."""

    rules_configuration = "complex_unit_rules"
    total_metric = "functions"


class SonarQubeLongUnits(SonarQubeViolationsWithPercentageScale):
    """SonarQube long methods/functions collector."""

    rules_configuration = "long_unit_rules"
    total_metric = "functions"


class SonarQubeManyParameters(SonarQubeViolationsWithPercentageScale):
    """SonarQube many parameters collector."""

    rules_configuration = "many_parameter_rules"
    total_metric = "functions"


class SonarQubeSuppressedViolations(SonarQubeViolations):
    """SonarQube suppressed violations collector."""

    rules_configuration = "suppression_rules"

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Get the suppressed violations from SonarQube.

        In addition to the suppressed rules, also get issues closed as false positive and won't fix from SonarQube
        as well as the total number of violations.
        """
        url = await SourceCollector._api_url(self)  # pylint: disable=protected-access
        component = self._parameter("component")
        branch = self._parameter("branch")
        all_issues_api_url = URL(f"{url}/api/issues/search?componentKeys={component}&branch={branch}")
        resolved_issues_api_url = URL(
            f"{all_issues_api_url}&status=RESOLVED&resolutions=WONTFIX,FALSE-POSITIVE&ps=500&"
            f"severities={self._violation_severities()}&types={self._violation_types()}"
        )
        return await super()._get_source_responses(*(urls + (resolved_issues_api_url, all_issues_api_url)))

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        measurement = await super()._parse_source_responses(responses[:-1])
        measurement.total = str((await responses[-1].json())["total"])
        return measurement

    async def _entity(self, issue) -> Entity:
        """Also add the resolution to the entity."""
        entity = await super()._entity(issue)
        resolution = issue.get("resolution", "").lower()
        entity["resolution"] = dict(wontfix="won't fix").get(resolution, resolution)
        return entity


class SonarQubeSecurityWarnings(SonarQubeViolations):
    """SonarQube security warnings. The security warnings are a sum of the vulnerabilities and security hotspots."""

    types_parameter = "security_types"

    async def _landing_url(self, responses: SourceResponses) -> URL:
        security_types = self._parameter(self.types_parameter)
        base_landing_url = await SourceCollector._landing_url(self, responses)  # pylint: disable=protected-access
        component = self._parameter("component")
        branch = self._parameter("branch")
        if "vulnerability" in security_types and "security_hotspot" in security_types:
            landing_url = f"{base_landing_url}/dashboard?id={component}&branch={branch}"
        elif "vulnerability" in security_types:
            landing_url = f"{base_landing_url}/project/issues?id={component}&resolved=false&branch={branch}"
        else:
            landing_url = f"{base_landing_url}/security_hotspots?id={component}&branch={branch}"
        return URL(landing_url)

    def _violation_types(self) -> str:
        return "VULNERABILITY"

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        api_urls = []
        security_types = self._parameter(self.types_parameter)
        component = self._parameter("component")
        branch = self._parameter("branch")
        base_url = await SonarQubeCollector._api_url(self)  # pylint: disable=protected-access
        if "vulnerability" in security_types:
            api_urls.append(
                URL(
                    f"{base_url}/api/issues/search?componentKeys={component}&resolved=false&ps=500&"
                    f"severities={self._violation_severities()}&types={self._violation_types()}&branch={branch}"
                )
            )
        if "security_hotspot" in security_types:
            api_urls.append(
                URL(f"{base_url}/api/hotspots/search?projectKey={component}&status=TO_REVIEW&ps=500&branch={branch}")
            )
        return await super()._get_source_responses(*api_urls)

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        security_types = self._parameter(self.types_parameter)
        vulnerabilities = (
            await super()._parse_source_responses(SourceResponses(responses=[responses[0]]))
            if "vulnerability" in security_types
            else SourceMeasurement()
        )
        if "security_hotspot" in security_types:
            json = await responses[-1].json()
            nr_hotspots = int(json.get("paging", {}).get("total", 0))
            hotspots = [await self.__entity(hotspot) for hotspot in json.get("hotspots", [])]
        else:
            nr_hotspots = 0
            hotspots = []
        return SourceMeasurement(
            value=str(int(vulnerabilities.value or 0) + nr_hotspots), entities=vulnerabilities.entities + hotspots
        )

    async def __entity(self, hotspot) -> Entity:
        """Create the security warning entity."""
        return Entity(
            key=hotspot["key"],
            component=hotspot["component"],
            message=hotspot["message"],
            type="security_hotspot",
            url=await self.__hotspot_landing_url(hotspot["key"]),
            vulnerability_probability=hotspot["vulnerabilityProbability"].lower(),
            creation_date=hotspot["creationDate"],
            update_date=hotspot["updateDate"],
        )

    async def __hotspot_landing_url(self, hotspot_key: str) -> URL:
        """Generate a landing url for the hotspot."""
        url = await SonarQubeCollector._landing_url(self, SourceResponses())  # pylint: disable=protected-access
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(f"{url}/security_hotspots?id={component}&hotspots={hotspot_key}&branch={branch}")


class SonarQubeMetricsBaseClass(SonarQubeCollector):
    """Base class for collectors that use the SonarQube measures/component API."""

    valueKey = ""  # Subclass responsibility
    totalKey = ""  # Subclass responsibility

    async def _landing_url(self, responses: SourceResponses) -> URL:
        url = await super()._landing_url(responses)
        component = self._parameter("component")
        branch = self._parameter("branch")
        metric = self._landing_url_metric_key()
        metric_parameter = f"&metric={metric}" if metric else ""
        return URL(f"{url}/component_measures?id={component}{metric_parameter}&branch={branch}")

    def _landing_url_metric_key(self) -> str:
        """Return the metric key to use for the landing url. This can be one key or an empty string."""
        return self._metric_keys().split(",")[0]

    async def _api_url(self) -> URL:
        url = await super()._api_url()
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(
            f"{url}/api/measures/component?component={component}&metricKeys={self._metric_keys()}&branch={branch}"
        )

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        metrics = await self.__get_metrics(responses)
        return SourceMeasurement(
            value=self._value(metrics), total=self._total(metrics), entities=await self._entities(metrics)
        )

    def _metric_keys(self) -> str:
        """Return the SonarQube metric keys to use."""
        value_key, total_key = self._value_key(), self._total_key()
        return f"{value_key},{total_key}" if total_key else value_key

    def _value(self, metrics: Dict[str, str]) -> str:
        """Return the metric value."""
        return str(sum(int(metrics[key]) for key in self._value_key().split(",")))

    def _total(self, metrics: Dict[str, str]) -> str:
        """Return the total value."""
        return metrics.get(self._total_key(), "100")

    async def _entities(self, metrics: Dict[str, str]) -> List[Entity]:  # pylint: disable=no-self-use,unused-argument
        """Return the entities."""
        return []

    def _value_key(self) -> str:
        """Return the SonarQube metric key(s) to use for the value. The string can be a comma-separated list of keys."""
        return self.valueKey

    def _total_key(self) -> str:
        """Return the SonarQube metric key to use for the total value."""
        return self.totalKey

    @staticmethod
    async def __get_metrics(responses: SourceResponses) -> Dict[str, str]:
        """Get the metric(s) from the responses."""
        measures = (await responses[0].json())["component"]["measures"]
        return {measure["metric"]: measure["value"] for measure in measures}


class SonarQubeDuplicatedLines(SonarQubeMetricsBaseClass):
    """SonarQube duplicated lines collector."""

    valueKey = "duplicated_lines"
    totalKey = "lines"


class SonarQubeLOC(SonarQubeMetricsBaseClass):
    """SonarQube lines of code."""

    LANGUAGES = dict(
        abap="ABAP",
        apex="Apex",
        c="C",
        cs="C#",
        cpp="C++",
        cobol="COBOL",
        css="CSS",
        flex="Flex",
        go="Go",
        web="HTML",
        jsp="JSP",
        java="Java",
        js="JavaScript",
        kotlin="Kotlin",
        objc="Objective-C",
        php="PHP",
        plsql="PL/SQL",
        py="Python",
        ruby="Ruby",
        scala="Scala",
        swift="Swift",
        tsql="T-SQL",
        ts="TypeScript",
        vbnet="VB.NET",
        xml="XML",
    )  # https://sonarcloud.io/api/languages/list

    def _value_key(self) -> str:
        return str(self._parameter("lines_to_count"))  # Either "lines" or "ncloc"

    def _metric_keys(self) -> str:
        metric_keys = super()._metric_keys()
        if self._value_key() == "ncloc":
            metric_keys += ",ncloc_language_distribution"  # Also get the ncloc per language
        return metric_keys

    def _value(self, metrics: Dict[str, str]) -> str:
        if self._value_key() == "ncloc":
            # Our user picked non-commented lines of code (ncloc), so we can sum the ncloc per language, skipping
            # languages the user wants to ignore
            return str(sum(int(ncloc) for _, ncloc in self.__language_ncloc(metrics)))
        return super()._value(metrics)

    async def _entities(self, metrics: Dict[str, str]) -> List[Entity]:
        if self._value_key() == "ncloc":
            # Our user picked non-commented lines of code (ncloc), so we can show the ncloc per language, skipping
            # languages the user wants to ignore
            return [
                Entity(key=language, language=self.LANGUAGES.get(language, language), ncloc=ncloc)
                for language, ncloc in self.__language_ncloc(metrics)
            ]
        return await super()._entities(metrics)

    def __language_ncloc(self, metrics: Dict[str, str]) -> List[List[str]]:
        """Return the languages and non-commented lines of code per language, ignoring languages if so specified."""
        languages_to_ignore = self._parameter("languages_to_ignore")
        return [
            language_count.split("=")
            for language_count in metrics["ncloc_language_distribution"].split(";")
            if not match_string_or_regular_expression(language_count.split("=")[0], languages_to_ignore)
        ]


class SonarQubeUncoveredLines(SonarQubeMetricsBaseClass):
    """SonarQube uncovered lines of code."""

    valueKey = "uncovered_lines"
    totalKey = "lines_to_cover"


class SonarQubeUncoveredBranches(SonarQubeMetricsBaseClass):
    """SonarQube uncovered branches."""

    valueKey = "uncovered_conditions"
    totalKey = "conditions_to_cover"


class SonarQubeRemediationEffort(SonarQubeMetricsBaseClass):
    """SonarQube violation (technical debt) remediation effort."""

    def _landing_url_metric_key(self) -> str:
        # The landing url can point to one metric, so if the user selected one effort type point the landing url to
        # that metric. If not, the landing url points to the project overview.
        effort_types = self.__effort_types()
        return effort_types[0] if len(effort_types) == 1 else ""

    def _value_key(self) -> str:
        return ",".join(self.__effort_types())

    async def _entities(self, metrics: Dict[str, str]) -> List[Entity]:
        entities = []
        api_values = self._data_model["sources"][self.source_type]["parameters"]["effort_types"]["api_values"]
        for effort_type in self.__effort_types():
            effort_type_description = [param for param, api_key in api_values.items() if effort_type == api_key][0]
            entities.append(
                Entity(
                    key=effort_type,
                    effort_type=effort_type_description,
                    effort=metrics[effort_type],
                    url=await self.__effort_type_landing_url(effort_type),
                )
            )
        return entities

    async def __effort_type_landing_url(self, effort_type: str) -> URL:
        """Generate a landing url for the effort type."""
        url = await super(SonarQubeMetricsBaseClass, self)._landing_url(  # pylint: disable=bad-super-call
            SourceResponses()
        )
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(f"{url}/component_measures?id={component}&metric={effort_type}&branch={branch}")

    def __effort_types(self) -> List[str]:
        """Return the user-selected effort types."""
        return list(self._parameter("effort_types"))


class SonarQubeTests(SonarQubeCollector):
    """SonarQube collector for the tests metric."""

    async def _api_url(self) -> URL:
        url = await super()._api_url()
        component = self._parameter("component")
        branch = self._parameter("branch")
        metric_keys = "tests,test_errors,test_failures,skipped_tests"
        return URL(f"{url}/api/measures/component?component={component}&metricKeys={metric_keys}&branch={branch}")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        url = await super()._landing_url(responses)
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(f"{url}/component_measures?id={component}&metric=tests&branch={branch}")

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        tests = await self.__nr_of_tests(responses)
        value = str(sum(tests[test_result] for test_result in self._parameter("test_result")))
        test_results = self._data_model["sources"][self.source_type]["parameters"]["test_result"]["values"]
        total = str(sum(tests[test_result] for test_result in test_results))
        return SourceMeasurement(value=value, total=total)

    @staticmethod
    async def __nr_of_tests(responses: SourceResponses) -> Dict[str, int]:
        """Return the number of tests by test result."""
        measures = {
            measure["metric"]: int(measure["value"]) for measure in (await responses[0].json())["component"]["measures"]
        }
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

    async def _landing_url(self, responses: SourceResponses) -> URL:
        url = await super()._landing_url(responses)
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(f"{url}/project/activity?id={component}&branch={branch}")

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        return isoparse((await response.json())["analyses"][0]["date"])
