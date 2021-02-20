"""Azure Devops Server tests collector."""

import itertools
from collections import defaultdict
from types import SimpleNamespace
from typing import Dict, List, cast

from base_collectors import SourceCollector
from collector_utilities.functions import match_string_or_regular_expression
from collector_utilities.type import URL
from source_model import Entity, SourceMeasurement, SourceResponses


class TestRun(SimpleNamespace):  # pylint: disable=too-few-public-methods
    """Represent an Azure DevOps test run."""

    def __init__(self, build_nr: int = 0) -> None:
        """Override to add test run attributes to the namespace."""
        super().__init__(build_nr=build_nr, test_count=0, total_test_count=0, entities=[])


class AzureDevopsTests(SourceCollector):
    """Collector for the tests metric."""

    async def _api_url(self) -> URL:
        """Extend to add the test run API path."""
        api_url = await super()._api_url()
        return URL(f"{api_url}/_apis/test/runs?automated=true&includeRunDetails=true&$api-version=5.0")

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the test runs."""
        test_results = cast(List[str], self._parameter("test_result"))
        test_run_names_to_include = cast(List[str], self._parameter("test_run_names_to_include")) or ["all"]
        test_run_states_to_include = [value.lower() for value in self._parameter("test_run_states_to_include")] or [
            "all"
        ]
        runs = (await responses[0].json()).get("value", [])
        highest_build: Dict[str, TestRun] = defaultdict(TestRun)
        for run in runs:
            name = run.get("name", "Unknown test run name")
            if test_run_names_to_include != ["all"] and not match_string_or_regular_expression(
                name, test_run_names_to_include
            ):
                continue
            state = run.get("state", "Unknown test run state")
            if test_run_states_to_include != ["all"] and state.lower() not in test_run_states_to_include:
                continue
            build_nr = int(run.get("build", {}).get("id", -1))
            if build_nr < highest_build[name].build_nr:
                continue
            if build_nr > highest_build[name].build_nr:
                highest_build[name] = TestRun(build_nr)
            counted_tests = sum(run.get(test_result, 0) for test_result in test_results)
            highest_build[name].test_count += counted_tests
            highest_build[name].total_test_count += run.get("totalTests", 0)
            highest_build[name].entities.append(
                Entity(
                    key=run["id"],
                    name=name,
                    state=state,
                    build_id=str(build_nr),
                    url=run.get("webAccessUrl", ""),
                    started_date=run.get("startedDate", ""),
                    completed_date=run.get("completedDate", ""),
                    counted_tests=str(counted_tests),
                    incomplete_tests=str(run.get("incompleteTests", 0)),
                    not_applicable_tests=str(run.get("notApplicableTests", 0)),
                    passed_tests=str(run.get("passedTests", 0)),
                    unanalyzed_tests=str(run.get("unanalyzedTests", 0)),
                    total_tests=str(run.get("totalTests", 0)),
                )
            )
        test_count = sum(build.test_count for build in highest_build.values())
        total_test_count = sum(build.total_test_count for build in highest_build.values())
        test_runs = list(itertools.chain.from_iterable([build.entities for build in highest_build.values()]))
        return SourceMeasurement(value=str(test_count), total=str(total_test_count), entities=test_runs)
