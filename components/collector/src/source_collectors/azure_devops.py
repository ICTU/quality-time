"""Azure Devops Server metric collector."""

from abc import ABC
from datetime import datetime
from typing import cast, List

from dateutil.parser import parse
import requests

from utilities.functions import days_ago
from utilities.type import Entities, Responses, URL, Value
from .source_collector import SourceCollector, UnmergedBranchesSourceCollector


class AzureDevopsBase(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for Azure DevOps collectors."""

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

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        if len(responses) < 2:
            return []  # We didn't get a response with work items, so assume there are none
        return [
            dict(
                key=str(work_item["id"]), project=work_item["fields"]["System.TeamProject"],
                title=work_item["fields"]["System.Title"], work_item_type=work_item["fields"]["System.WorkItemType"],
                state=work_item["fields"]["System.State"],
                url=work_item["url"]) for work_item in responses[1].json()["value"]]


class AzureDevopsIssues(AzureDevopsBase):
    """Collector to get issues from Azure Devops Server."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(len(responses[0].json()["workItems"]))


class AzureDevopsReadyUserStoryPoints(AzureDevopsBase):
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


class AzureDevopsUnmergedBranches(UnmergedBranchesSourceCollector):
    """Collector for unmerged branches."""

    def _api_url(self) -> URL:
        url = super()._api_url()
        project = str(url).split("/")[-1]
        return URL(f"{url}/_apis/git/repositories/{project}/stats/branches?api-version=4.1")

    def _unmerged_branches(self, responses: Responses) -> List:
        return [branch for branch in responses[0].json()["value"] if not branch["isBaseVersion"] and
                int(branch["aheadCount"]) > 0 and
                self._commit_age(branch).days > int(cast(str, self._parameter("inactive_days")))]

    def _commit_datetime(self, branch) -> datetime:
        return parse(branch["commit"]["committer"]["date"])


class AzureDevopsSourceUpToDateness(SourceCollector):
    """Collector class to measure the up-to-dateness of a repo or folder/file in a repo."""

    def _api_url(self) -> URL:
        api_url = str(super()._api_url())
        repository = self._parameter("repository")
        repositories_url = f"{api_url}/_apis/git/repositories?api-version=4.1"
        repositories = requests.get(repositories_url, timeout=self.TIMEOUT, auth=self._basic_auth_credentials())
        repositories.raise_for_status()
        repository_id = [r for r in repositories.json()["value"] if repository in (r["name"], r["id"])][0]["id"]
        path = self._parameter("file_path", quote=True)
        branch = self._parameter("branch", quote=True)
        search_criteria = \
            f"searchCriteria.itemPath={path}&searchCriteria.itemVersion.version={branch}&searchCriteria.$top=1"
        return URL(f"{api_url}/_apis/git/repositories/{repository_id}/commits?{search_criteria}&api-version=4.1")

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
