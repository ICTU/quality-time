"""Azure DevOps Server base classes for collectors."""

import urllib.parse
from abc import ABC
from datetime import datetime

from base_collectors import SourceCollector
from collector_utilities.date_time import parse_datetime
from collector_utilities.exceptions import NotFoundError
from collector_utilities.functions import match_string_or_regular_expression
from collector_utilities.type import URL, Job
from model import Entities, Entity, SourceResponses


class AzureDevopsRepositoryBase(SourceCollector, ABC):
    """Base class for Azure DevOps collectors that work with repositories."""

    async def _api_url(self) -> URL:
        """Extend to add the repository."""
        api_url = str(await super()._api_url())
        return URL(f"{api_url}/_apis/git/repositories/{await self.__repository_id()}")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the repository."""
        landing_url = str(await super()._landing_url(responses))
        repository = self._parameter("repository") or landing_url.rsplit("/", 1)[-1]
        return URL(f"{landing_url}/_git/{repository}")

    async def __repository_id(self) -> str:
        """Return the repository id belonging to the repository."""
        api_url = str(await super()._api_url())
        repository = self._parameter("repository") or urllib.parse.unquote(api_url.rsplit("/", 1)[-1])
        repositories_url = URL(f"{api_url}/_apis/git/repositories?api-version=4.1")
        repositories = (await (await super()._get_source_responses(repositories_url))[0].json())["value"]
        matching_repositories = [r for r in repositories if repository in (r["name"], r["id"])]
        if not matching_repositories:
            raise NotFoundError(type_of_thing="Repository", name_of_thing=str(repository))
        return str(matching_repositories[0]["id"])


class AzureDevopsJobs(SourceCollector):
    """Base class for job collectors."""

    async def _api_url(self) -> URL:
        """Extend to add the build definitions API path."""
        return URL(f"{await super()._api_url()}/_apis/build/definitions?includeLatestBuilds=true&api-version=4.1")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Override to add the builds path."""
        return URL(f"{await super()._api_url()}/_build")

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the jobs."""
        entities = Entities()
        for job in (await responses[0].json())["value"]:
            if not job.get("latestCompletedBuild", {}).get("result"):
                continue  # The job has no completed builds
            name = self.__job_name(job)
            url = job["_links"]["web"]["href"]
            build_status = self._latest_build_result(job)
            build_dt_str = ""  # sadly, mypy does not understand short-circuiting this
            if build_dt := self._latest_build_date_time(job):
                build_dt_str = str(build_dt.date())
            entities.append(
                Entity(
                    key=name,
                    name=name,
                    url=url,
                    build_date=build_dt_str,
                    build_status=build_status,
                ),
            )
        return entities

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether this job should be included."""
        jobs_to_include = self._parameter("jobs_to_include")
        if len(jobs_to_include) > 0 and not match_string_or_regular_expression(entity["name"], jobs_to_include):
            return False
        return not match_string_or_regular_expression(entity["name"], self._parameter("jobs_to_ignore"))

    @staticmethod
    def _latest_build_result(job: Job) -> str:
        """Return the result of the latest build."""
        return str(job["latestCompletedBuild"]["result"])

    @staticmethod
    def _latest_build_date_time(job: Job) -> datetime | None:
        """Return the finish time of the latest build of the job."""
        return (
            parse_datetime(job["latestCompletedBuild"]["finishTime"])
            if "finishTime" in job["latestCompletedBuild"]
            else None
        )

    @staticmethod
    def __job_name(job: Job) -> str:
        """Return the job name."""
        return "/".join([*job["path"].strip("\\").split("\\"), job["name"]]).strip("/")


class AzureDevopsPipelines(SourceCollector):
    """Base class for pipeline collectors."""

    async def _api_url(self) -> URL:
        """Extend to add the pipelines API path."""
        # currently the pipelines api is not available in any version which is not a -preview version
        return URL(f"{await super()._api_url()}/_apis/pipelines?api-version=6.0-preview.1")

    async def _api_runs_url(self, pipeline_id: int) -> URL:
        """Extend to add the pipeline runs API path."""
        split_api_url = urllib.parse.urlsplit(await self._api_url())
        new_api_url_parts = split_api_url._replace(path=f"{split_api_url[2]}/{pipeline_id}/runs")
        return URL(urllib.parse.urlunsplit(new_api_url_parts))

    async def _active_pipelines(self) -> list[int]:
        """Find all active pipeline ids to traverse."""
        api_pipelines_url = await self._api_url()
        pipelines_response = await super()._get_source_responses(api_pipelines_url)
        pipelines = (await pipelines_response[0].json())["value"]
        return [pipeline["id"] for pipeline in pipelines if "id" in pipeline]

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Override because we need to first query the pipeline ids to separately get the entities."""
        pipeline_ids = await self._active_pipelines()
        api_pipelines_urls = [await self._api_runs_url(pipeline_id) for pipeline_id in pipeline_ids]
        return await super()._get_source_responses(*api_pipelines_urls)

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the pipelines."""
        entities = Entities()
        for pipeline_response in responses:
            for pipeline_run in (await pipeline_response.json())["value"]:
                if not bool(pipeline_run.get("finishedDate")):
                    continue  # The pipeline has not completed

                pipeline_id = pipeline_run["pipeline"]["id"]
                pipeline_name = pipeline_run["pipeline"]["name"]
                entities.append(
                    Entity(
                        key="-".join([str(pipeline_id), pipeline_run["name"]]),
                        name=pipeline_run["name"],
                        pipeline=pipeline_name,
                        url=pipeline_run["_links"]["web"]["href"],
                        build_date=str(parse_datetime(pipeline_run["finishedDate"]).date()),
                        build_status=pipeline_run["state"],
                    ),
                )
        return entities

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether this pipeline should be included."""
        jobs_to_include = self._parameter("jobs_to_include")
        if len(jobs_to_include) > 0 and not match_string_or_regular_expression(entity["pipeline"], jobs_to_include):
            return False
        return not match_string_or_regular_expression(entity["pipeline"], self._parameter("jobs_to_ignore"))
