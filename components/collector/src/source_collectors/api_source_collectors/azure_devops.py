"""Azure Devops Server metric collector.

Where possible we use version 4.1 of the API so we can support TFS 2018 and newer.
See https://docs.microsoft.com/en-gb/rest/api/azure/devops/?view=azure-devops-rest-4.1#api-and-tfs-version-mapping
"""

import itertools
import urllib.parse
from abc import ABC
from collections import defaultdict
from datetime import datetime
from types import SimpleNamespace
from typing import Any, Dict, Final, List, cast

import aiohttp
from dateutil.parser import parse

from base_collectors import SourceCollector, SourceUpToDatenessCollector, UnmergedBranchesSourceCollector
from collector_utilities.functions import days_ago, match_string_or_regular_expression
from collector_utilities.type import URL, Job, Response
from source_model import Entity, SourceMeasurement, SourceResponses


class AzureDevopsIssues(SourceCollector):
    """Collector to get issues from Azure Devops Server."""

    MAX_IDS_PER_WORK_ITEMS_API_CALL: Final[int] = 200  # See
    # https://docs.microsoft.com/en-us/rest/api/azure/devops/wit/work%20items/list?view=azure-devops-rest-5.1

    async def _api_url(self) -> URL:
        """Extend to add the WIQL API path."""
        return URL(f"{await super()._api_url()}/_apis/wit/wiql?api-version=4.1")

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Override because we need to do a post request and need to separately get the entities."""
        api_url = urls[0]
        auth = aiohttp.BasicAuth(str(self._parameter("private_token")))
        response = await self._session.post(api_url, auth=auth, json=dict(query=self._parameter("wiql")))
        ids = [str(work_item["id"]) for work_item in (await response.json()).get("workItems", [])]
        if not ids:
            return SourceResponses(responses=[response], api_url=api_url)
        ids_string = ",".join(ids[: min(self.MAX_IDS_PER_WORK_ITEMS_API_CALL, SourceMeasurement.MAX_ENTITIES)])
        work_items_url = URL(f"{await super()._api_url()}/_apis/wit/workitems?ids={ids_string}&api-version=4.1")
        work_items = await super()._get_source_responses(work_items_url)
        work_items.insert(0, response)
        return work_items

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the work items from the WIQL query response."""
        value = str(len((await responses[0].json())["workItems"]))
        entities = [
            Entity(
                key=work_item["id"],
                project=work_item["fields"]["System.TeamProject"],
                title=work_item["fields"]["System.Title"],
                work_item_type=work_item["fields"]["System.WorkItemType"],
                state=work_item["fields"]["System.State"],
                url=work_item["url"],
            )
            for work_item in await self._work_items(responses)
        ]
        return SourceMeasurement(value=value, entities=entities)

    @staticmethod
    async def _work_items(responses: SourceResponses):
        """Return the work items, if any."""
        return (await responses[1].json())["value"] if len(responses) > 1 else []


class AzureDevopsUserStoryPoints(AzureDevopsIssues):
    """Collector to get user story points from Azure Devops Server."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the story points from the work items."""
        measurement = await super()._parse_source_responses(responses)
        value = 0
        for entity, work_item in zip(measurement.entities, await self._work_items(responses)):
            entity["story_points"] = story_points = work_item["fields"].get("Microsoft.VSTS.Scheduling.StoryPoints")
            value += 0 if story_points is None else story_points
        measurement.value = str(round(value))
        return measurement


class AzureDevopsRepositoryBase(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for Azure DevOps collectors that work with repositories."""

    async def _repository_id(self) -> str:
        """Return the repository id belonging to the repository."""
        api_url = str(await super()._api_url())
        repository = self._parameter("repository") or urllib.parse.unquote(api_url.rsplit("/", 1)[-1])
        repositories_url = URL(f"{api_url}/_apis/git/repositories?api-version=4.1")
        repositories = (await (await super()._get_source_responses(repositories_url))[0].json())["value"]
        return str([r for r in repositories if repository in (r["name"], r["id"])][0]["id"])


class AzureDevopsUnmergedBranches(UnmergedBranchesSourceCollector, AzureDevopsRepositoryBase):
    """Collector for unmerged branches."""

    async def _api_url(self) -> URL:
        """Extend to add the branches API path."""
        api_url = str(await super()._api_url())
        return URL(f"{api_url}/_apis/git/repositories/{await self._repository_id()}/stats/branches?api-version=4.1")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the branches path."""
        landing_url = str(await super()._landing_url(responses))
        repository = self._parameter("repository") or landing_url.rsplit("/", 1)[-1]
        return URL(f"{landing_url}/_git/{repository}/branches")

    async def _unmerged_branches(self, responses: SourceResponses) -> List[Dict[str, Any]]:
        """Override to get the unmerged branches response.

        Branches are considered unmerged if they have a base branch, have commits that are not on the base branch,
        have not been committed to for a minimum number of days, and are not to be ignored.
        """
        return [
            branch
            for branch in (await responses[0].json())["value"]
            if not branch["isBaseVersion"]
            and int(branch["aheadCount"]) > 0
            and days_ago(self._commit_datetime(branch)) > int(cast(str, self._parameter("inactive_days")))
            and not match_string_or_regular_expression(branch["name"], self._parameter("branches_to_ignore"))
        ]

    def _commit_datetime(self, branch) -> datetime:
        """Override to get the date and time of the most recent commit."""
        return parse(branch["commit"]["committer"]["date"])

    def _branch_landing_url(self, branch) -> URL:
        """Override to return the landing URL for the branch."""
        return URL(branch["commit"]["url"])


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


class AzureDevopsJobs(SourceCollector):
    """Base class for job collectors."""

    async def _api_url(self) -> URL:
        """Extend to add the build definitions API path."""
        return URL(f"{await super()._api_url()}/_apis/build/definitions?includeLatestBuilds=true&api-version=4.1")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Override to add the builds path."""
        return URL(f"{await super()._api_url()}/_build")

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the jobs/pipelines."""
        entities = []
        for job in (await responses[0].json())["value"]:
            if not self._include_job(job):
                continue
            name = self.__job_name(job)
            url = job["_links"]["web"]["href"]
            build_status = self._latest_build_result(job)
            build_date_time = self._latest_build_date_time(job)
            entities.append(
                Entity(key=name, name=name, url=url, build_date=str(build_date_time.date()), build_status=build_status)
            )
        return SourceMeasurement(entities=entities)

    def _include_job(self, job: Job) -> bool:
        """Return whether this job should be included."""
        if not job.get("latestCompletedBuild", {}).get("result"):
            return False  # The job has no completed builds
        jobs_to_include = self._parameter("jobs_to_include")
        if len(jobs_to_include) > 0 and not match_string_or_regular_expression(job["name"], jobs_to_include):
            return False
        return not match_string_or_regular_expression(self.__job_name(job), self._parameter("jobs_to_ignore"))

    @staticmethod
    def _latest_build_result(job: Job) -> str:
        """Return the result of the latest build."""
        return str(job["latestCompletedBuild"]["result"])

    @staticmethod
    def _latest_build_date_time(job: Job) -> datetime:
        """Return the finish time of the latest build of the job."""
        return parse(job["latestCompletedBuild"]["finishTime"])

    @staticmethod
    def __job_name(job: Job) -> str:
        """Return the job name."""
        return "/".join(job["path"].strip(r"\\").split(r"\\") + [job["name"]]).strip("/")


class AzureDevopsFailedJobs(AzureDevopsJobs):
    """Collector for the failed jobs metric."""

    def _include_job(self, job: Job) -> bool:
        """Extend to check for failure type."""
        if not super()._include_job(job):
            return False
        return self._latest_build_result(job) in self._parameter("failure_type")


class AzureDevopsUnusedJobs(AzureDevopsJobs):
    """Collector for the unused jobs metric."""

    def _include_job(self, job: Job) -> bool:
        """Extend to filter unused jobs."""
        if not super()._include_job(job):
            return False
        max_days = int(cast(str, self._parameter("inactive_job_days")))
        actual_days = days_ago(self._latest_build_date_time(job))
        return actual_days > max_days


class AzureDevopsFileUpToDateness(SourceUpToDatenessCollector, AzureDevopsRepositoryBase):
    """Collector class to measure the up-to-dateness of a repo or folder/file in a repo."""

    async def _api_url(self) -> URL:
        """Extend to add the commit API path and associated parameters."""
        api_url = str(await super()._api_url())
        repository_id = await self._repository_id()
        path = self._parameter("file_path", quote=True)
        branch = self._parameter("branch", quote=True)
        search_criteria = (
            f"searchCriteria.itemPath={path}&searchCriteria.itemVersion.version={branch}&searchCriteria.$top=1"
        )
        return URL(f"{api_url}/_apis/git/repositories/{repository_id}/commits?{search_criteria}&api-version=4.1")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add a path to the file."""
        landing_url = str(await super()._landing_url(responses))
        repository = self._parameter("repository") or landing_url.rsplit("/", 1)[-1]
        path = self._parameter("file_path", quote=True)
        branch = self._parameter("branch", quote=True)
        return URL(f"{landing_url}/_git/{repository}?path={path}&version=GB{branch}")

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to get the date and time of the commit or the pipeline."""
        json_value = (await response.json())["value"]
        return parse(json_value[0]["committer"]["date"])


class AzureDevopsJobUpToDateness(SourceUpToDatenessCollector, AzureDevopsJobs):
    """Collector class to measure the up-to-dateness of a job/pipeline."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to get the date and time of the commit or the pipeline."""
        json_value = (await response.json())["value"]
        build_date_times = [self._latest_build_date_time(job) for job in json_value if self._include_job(job)]
        return max(build_date_times, default=datetime.min)


class AzureDevopsSourceUpToDateness(SourceCollector, ABC):
    """Factory class to create a collector to get the up-to-dateness of either jobs or files."""

    def __new__(cls, session: aiohttp.ClientSession, source, data_model):
        """Create an instance of either the file up-to-dateness collector or the jobs up-to-dateness collector."""
        jobs_to_include = source.get("parameters", {}).get("jobs_to_include", [])
        collector_class = AzureDevopsJobUpToDateness if len(jobs_to_include) > 0 else AzureDevopsFileUpToDateness
        instance = collector_class(session, source, data_model)
        instance.source_type = cls.source_type
        return instance

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to document that this class does not parse responses itself."""
        raise NotImplementedError
