"""Azure Devops Server metric collector.

Where possible we use version 4.1 of the API so we can support TFS 2018 and newer.
See https://docs.microsoft.com/en-gb/rest/api/azure/devops/?view=azure-devops-rest-4.1#api-and-tfs-version-mapping
"""

from abc import ABC
from datetime import datetime
from typing import cast, Any, Dict, Final, List, Tuple

from dateutil.parser import parse
import aiohttp

from collector_utilities.functions import days_ago, match_string_or_regular_expression
from collector_utilities.type import Entities, Job, Response, Responses, URL, Value
from base_collectors import SourceCollector, SourceUpToDatenessCollector, UnmergedBranchesSourceCollector


class AzureDevopsIssues(SourceCollector):
    """Collector to get issues from Azure Devops Server."""

    MAX_IDS_PER_WORK_ITEMS_API_CALL: Final[int] = 200  # See
    # https://docs.microsoft.com/en-us/rest/api/azure/devops/wit/work%20items/list?view=azure-devops-rest-5.1

    async def _api_url(self) -> URL:
        return URL(f"{await super()._api_url()}/_apis/wit/wiql?api-version=4.1")

    async def _get_source_responses(self, *urls: URL) -> Responses:
        """Override because we need to do a post request and need to separately get the entities."""
        auth = aiohttp.BasicAuth(str(self._parameter("private_token")))
        response = await self._session.post(urls[0], auth=auth, json=dict(query=self._parameter("wiql")))
        ids = [str(work_item["id"]) for work_item in (await response.json()).get("workItems", [])]
        if not ids:
            return [response]
        ids_string = ",".join(ids[:min(self.MAX_IDS_PER_WORK_ITEMS_API_CALL, self.MAX_ENTITIES)])
        work_items_url = URL(f"{await super()._api_url()}/_apis/wit/workitems?ids={ids_string}&api-version=4.1")
        work_items = await super()._get_source_responses(work_items_url)
        return [response] + work_items

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        value = str(len((await responses[0].json())["workItems"]))
        entities = [
            dict(
                key=str(work_item["id"]), project=work_item["fields"]["System.TeamProject"],
                title=work_item["fields"]["System.Title"], work_item_type=work_item["fields"]["System.WorkItemType"],
                state=work_item["fields"]["System.State"], url=work_item["url"])
            for work_item in await self._work_items(responses)]
        return value, "100", entities

    @staticmethod
    async def _work_items(responses: Responses):
        """Return the work items, if any."""
        return (await responses[1].json())["value"] if len(responses) > 1 else []


class AzureDevopsReadyUserStoryPoints(AzureDevopsIssues):
    """Collector to get ready user story points from Azure Devops Server."""

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        _, total, entities = await super()._parse_source_responses(responses)
        value = 0
        for entity, work_item in zip(entities, await self._work_items(responses)):
            entity["story_points"] = story_points = work_item["fields"].get("Microsoft.VSTS.Scheduling.StoryPoints")
            value += 0 if story_points is None else story_points
        return str(round(value)), total, entities


class AzureDevopsRepositoryBase(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for Azure DevOps collectors that work with repositories."""

    async def _repository_id(self) -> str:
        """Return the repository id belonging to the repository."""
        api_url = str(await super()._api_url())
        repository = self._parameter("repository") or api_url.rsplit("/", 1)[-1]
        repositories_url = URL(f"{api_url}/_apis/git/repositories?api-version=4.1")
        repositories = (await (await super()._get_source_responses(repositories_url))[0].json())["value"]
        return str([r for r in repositories if repository in (r["name"], r["id"])][0]["id"])


class AzureDevopsUnmergedBranches(UnmergedBranchesSourceCollector, AzureDevopsRepositoryBase):
    """Collector for unmerged branches."""

    async def _api_url(self) -> URL:
        api_url = str(await super()._api_url())
        return URL(f"{api_url}/_apis/git/repositories/{await self._repository_id()}/stats/branches?api-version=4.1")

    async def _landing_url(self, responses: Responses) -> URL:
        landing_url = str(await super()._landing_url(responses))
        repository = self._parameter("repository") or landing_url.rsplit("/", 1)[-1]
        return URL(f"{landing_url}/_git/{repository}/branches")

    async def _unmerged_branches(self, responses: Responses) -> List[Dict[str, Any]]:
        return [branch for branch in (await responses[0].json())["value"] if not branch["isBaseVersion"] and
                int(branch["aheadCount"]) > 0 and
                days_ago(self._commit_datetime(branch)) > int(cast(str, self._parameter("inactive_days"))) and
                not match_string_or_regular_expression(branch["name"], self._parameter("branches_to_ignore"))]

    def _commit_datetime(self, branch) -> datetime:
        return parse(branch["commit"]["committer"]["date"])


class AzureDevopsSourceUpToDateness(SourceUpToDatenessCollector, AzureDevopsRepositoryBase):
    """Collector class to measure the up-to-dateness of a repo or folder/file in a repo."""

    async def _api_url(self) -> URL:
        api_url = str(await super()._api_url())
        repository_id = await self._repository_id()
        path = self._parameter("file_path", quote=True)
        branch = self._parameter("branch", quote=True)
        search_criteria = \
            f"searchCriteria.itemPath={path}&searchCriteria.itemVersion.version={branch}&searchCriteria.$top=1"
        return URL(f"{api_url}/_apis/git/repositories/{repository_id}/commits?{search_criteria}&api-version=4.1")

    async def _landing_url(self, responses: Responses) -> URL:
        landing_url = str(await super()._landing_url(responses))
        repository = self._parameter("repository") or landing_url.rsplit("/", 1)[-1]
        path = self._parameter("file_path", quote=True)
        branch = self._parameter("branch", quote=True)
        return URL(f"{landing_url}/_git/{repository}?path={path}&version=GB{branch}")

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        return parse((await response.json())["value"][0]["committer"]["date"])


class AzureDevopsTests(SourceCollector):
    """Collector for the tests metric."""

    async def _api_url(self) -> URL:
        api_url = await super()._api_url()
        return URL(f"{api_url}/_apis/test/runs?automated=true&includeRunDetails=true&$top=1&api-version=5.1")

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        test_results = cast(List[str], self._parameter("test_result"))
        runs = (await responses[0].json()).get("value", [])
        test_count, highest_build_nr_seen = 0, 0
        for run in runs:
            build_nr = int(run.get("build", {}).get("id", "-1"))
            if build_nr < highest_build_nr_seen:
                continue
            if build_nr > highest_build_nr_seen:
                highest_build_nr_seen = build_nr
                test_count = 0
            test_count += sum(run.get(test_result, 0) for test_result in test_results)
        return str(test_count), "100", []


class AzureDevopsJobs(SourceCollector):
    """Base class for job collectors."""

    async def _api_url(self) -> URL:
        return URL(f"{await super()._api_url()}/_apis/build/definitions?includeLatestBuilds=true&api-version=4.1")

    async def _landing_url(self, responses: Responses) -> URL:
        return URL(f"{await super()._api_url()}/_build")

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        entities: Entities = []
        for job in (await responses[0].json())["value"]:
            if self._ignore_job(job):
                continue
            name = self.__job_name(job)
            url = job["_links"]["web"]["href"]
            build_status = self._latest_build_result(job)
            build_date_time = self._latest_build_date_time(job)
            entities.append(
                dict(name=name, key=name, url=url,
                     build_date=str(build_date_time.date()),
                     build_age=str(days_ago(build_date_time)),
                     build_status=build_status))
        return str(len(entities)), "100", entities

    def _ignore_job(self, job: Job) -> bool:
        """Return whether this job should be ignored"""
        if not job.get("latestCompletedBuild", {}).get("result"):
            return True  # The job has no completed builds
        return match_string_or_regular_expression(self.__job_name(job), self._parameter("jobs_to_ignore"))

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

    def _ignore_job(self, job: Job) -> bool:
        if super()._ignore_job(job):
            return True
        return self._latest_build_result(job) not in self._parameter("failure_type")


class AzureDevopsUnusedJobs(AzureDevopsJobs):
    """Collector for the unused jobs metric."""

    def _ignore_job(self, job: Job) -> bool:
        if super()._ignore_job(job):
            return True
        max_days = int(cast(str, self._parameter("inactive_job_days")))
        actual_days = days_ago(self._latest_build_date_time(job))
        return actual_days <= max_days
