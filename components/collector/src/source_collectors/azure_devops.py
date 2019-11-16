"""Azure Devops Server metric collector.

Where possible we use version 4.1 of the API so we can support TFS 2018 and newer.
See https://docs.microsoft.com/en-gb/rest/api/azure/devops/?view=azure-devops-rest-4.1#api-and-tfs-version-mapping
"""

from abc import ABC
from datetime import datetime, date
from typing import cast, List

from dateutil.parser import parse
import requests

from collector_utilities.functions import days_ago, match_string_or_regular_expression
from collector_utilities.type import Entities, Job, Responses, URL, Value
from .source_collector import SourceCollector, UnmergedBranchesSourceCollector


class AzureDevopsIssues(SourceCollector):
    """Collector to get issues from Azure Devops Server."""

    MAX_IDS_PER_WORKITEMS_API_CALL = 200  # See
    # https://docs.microsoft.com/en-us/rest/api/azure/devops/wit/work%20items/list?view=azure-devops-rest-5.1

    def _api_url(self) -> URL:
        url = super()._api_url()
        return URL(f"{url}/_apis/wit/wiql?api-version=4.1")

    def _get_source_responses(self, api_url: URL) -> Responses:
        """Override because we need to do a post request and need to separately get the entities."""
        auth = self._basic_auth_credentials()
        response = requests.post(api_url, timeout=self.TIMEOUT, auth=auth, json=dict(query=self._parameter("wiql")))
        ids = [str(work_item["id"]) for work_item in response.json().get("workItems", [])]
        if not ids:
            return [response]
        ids_string = ",".join(ids[:min(self.MAX_IDS_PER_WORKITEMS_API_CALL, self.MAX_ENTITIES)])
        work_items_url = URL(f"{super()._api_url()}/_apis/wit/workitems?ids={ids_string}&api-version=4.1")
        return [response, requests.get(work_items_url, timeout=self.TIMEOUT, auth=auth)]

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(len(responses[0].json()["workItems"]))

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        if len(responses) < 2:
            return []  # We didn't get a response with work items, so assume there are none
        return [
            dict(
                key=str(work_item["id"]), project=work_item["fields"]["System.TeamProject"],
                title=work_item["fields"]["System.Title"], work_item_type=work_item["fields"]["System.WorkItemType"],
                state=work_item["fields"]["System.State"],
                url=work_item["url"]) for work_item in responses[1].json()["value"]]


class AzureDevopsReadyUserStoryPoints(AzureDevopsIssues):
    """Collector to get ready user story points from Azure Devops Server."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(round(sum(
            [work_item["fields"].get("Microsoft.VSTS.Scheduling.StoryPoints", 0)
             for work_item in responses[1].json()["value"]]))) if len(responses) > 1 else "0"

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        entities = super()._parse_source_responses_entities(responses)
        # Add story points to the entities:
        if len(responses) > 1:
            for entity, work_item in zip(entities, responses[1].json()["value"]):
                entity["story_points"] = work_item["fields"].get("Microsoft.VSTS.Scheduling.StoryPoints")
        return entities


class AzureDevopsRepositoryBase(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for Azure DevOps collectors that work with repositories."""

    def _repository_id(self) -> str:
        """Return the repository id belonging to the repository."""
        api_url = str(super()._api_url())
        repository = self._parameter("repository") or api_url.rsplit("/", 1)[-1]
        repositories_url = f"{api_url}/_apis/git/repositories?api-version=4.1"
        repositories = requests.get(repositories_url, timeout=self.TIMEOUT, auth=self._basic_auth_credentials())
        repositories.raise_for_status()
        return str([r for r in repositories.json()["value"] if repository in (r["name"], r["id"])][0]["id"])


class AzureDevopsUnmergedBranches(UnmergedBranchesSourceCollector, AzureDevopsRepositoryBase):
    """Collector for unmerged branches."""

    def _api_url(self) -> URL:
        api_url = str(super()._api_url())
        return URL(f"{api_url}/_apis/git/repositories/{self._repository_id()}/stats/branches?api-version=4.1")

    def _landing_url(self, responses: Responses) -> URL:
        landing_url = str(super()._landing_url(responses))
        repository = self._parameter("repository") or landing_url.rsplit("/", 1)[-1]
        return URL(f"{landing_url}/_git/{repository}/branches")

    def _unmerged_branches(self, responses: Responses) -> List:
        return [branch for branch in responses[0].json()["value"] if not branch["isBaseVersion"] and
                int(branch["aheadCount"]) > 0 and
                self._commit_age(branch).days > int(cast(str, self._parameter("inactive_days")))]

    def _commit_datetime(self, branch) -> datetime:
        return parse(branch["commit"]["committer"]["date"])


class AzureDevopsSourceUpToDateness(AzureDevopsRepositoryBase):
    """Collector class to measure the up-to-dateness of a repo or folder/file in a repo."""

    def _api_url(self) -> URL:
        api_url = str(super()._api_url())
        repository_id = self._repository_id()
        path = self._parameter("file_path", quote=True)
        branch = self._parameter("branch", quote=True)
        search_criteria = \
            f"searchCriteria.itemPath={path}&searchCriteria.itemVersion.version={branch}&searchCriteria.$top=1"
        return URL(f"{api_url}/_apis/git/repositories/{repository_id}/commits?{search_criteria}&api-version=4.1")

    def _landing_url(self, responses: Responses) -> URL:
        landing_url = str(super()._landing_url(responses))
        repository = self._parameter("repository") or landing_url.rsplit("/", 1)[-1]
        path = self._parameter("file_path", quote=True)
        branch = self._parameter("branch", quote=True)
        return URL(f"{landing_url}/_git/{repository}?path={path}&version=GB{branch}")

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(days_ago(parse(responses[0].json()["value"][0]["committer"]["date"])))


class AzureDevopsTests(SourceCollector):
    """Collector for the tests metric."""

    def _api_url(self) -> URL:
        return URL(f"{super()._api_url()}/_apis/test/runs?automated=true&includeRunDetails=true&$top=1&api-version=5.1")

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        test_results = cast(List[str], self._parameter("test_result"))
        runs = responses[0].json().get("value", [])
        test_count, highest_build_nr_seen = 0, 0
        for run in runs:
            build_nr = int(run.get("build", {}).get("id", "-1"))
            if build_nr < highest_build_nr_seen:
                continue
            if build_nr > highest_build_nr_seen:
                highest_build_nr_seen = build_nr
                test_count = 0
            test_count += sum(run.get(test_result, 0) for test_result in test_results)
        return str(test_count)


class AxureDevopsJobs(SourceCollector):
    """Base class for job collectors."""

    def _api_url(self) -> URL:
        return URL(f"{super()._api_url()}/_apis/build/definitions?includeLatestBuilds=true&api-version=4.1")

    def _landing_url(self, responses: Responses) -> URL:
        return URL(f"{super()._api_url()}/_build")

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(len(self._parse_source_responses_entities(responses)))

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        entities: Entities = []
        for job in responses[0].json()["value"]:
            if self._ignore_job(job):
                continue
            name = self.__job_name(job)
            url = job["_links"]["web"]["href"]
            build_status = job["latestCompletedBuild"]["result"]
            build_date = parse(job["latestCompletedBuild"]["finishTime"]).date()
            build_age = (date.today() - build_date).days
            entities.append(
                dict(name=name, key=name, url=url, build_date=str(build_date), build_age=str(build_age),
                     build_status=build_status))
        return entities

    def _ignore_job(self, job: Job) -> bool:
        """Return whether this job should be ignored"""
        if not job.get("latestCompletedBuild", {}).get("result"):
            return True  # The job has no completed builds
        return match_string_or_regular_expression(self.__job_name(job), self._parameter("jobs_to_ignore"))

    @staticmethod
    def __job_name(job: Job) -> str:
        """Return the job name."""
        return "/".join(job["path"].strip(r"\\").split(r"\\") + [job["name"]]).strip("/")


class AzureDevopsFailedJobs(AxureDevopsJobs):
    """Collector for the failed jobs metric."""

    def _ignore_job(self, job: Job) -> bool:
        if super()._ignore_job(job):
            return True
        return job["latestCompletedBuild"]["result"] not in self._parameter("failure_type")


class AzureDevopsUnusedJobs(AxureDevopsJobs):
    """Collector for the unused jobs metric."""

    def _ignore_job(self, job: Job) -> bool:
        if super()._ignore_job(job):
            return True
        max_days = int(cast(str, self._parameter("inactive_job_days")))
        build_date = parse(job["latestCompletedBuild"]["finishTime"]).date()
        build_age = (date.today() - build_date).days
        return build_age <= max_days
