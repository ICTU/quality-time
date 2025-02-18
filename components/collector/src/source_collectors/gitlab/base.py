"""GitLab collector base classes."""

from abc import ABC
from dataclasses import dataclass, fields
from datetime import datetime, timedelta
from typing import cast

from dateutil.tz import tzutc

from shared.utils.date_time import now

from base_collectors import SourceCollector
from collector_utilities.date_time import parse_datetime
from collector_utilities.exceptions import CollectorError
from collector_utilities.functions import add_query, match_string_or_regular_expression
from collector_utilities.type import URL, Job
from model import Entities, Entity, SourceResponses


class GitLabBase(SourceCollector, ABC):
    """Base class for GitLab collectors."""

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to follow GitLab pagination links, if necessary."""
        all_responses = responses = await super()._get_source_responses(*urls)
        while next_urls := await self._next_urls(responses):
            # Retrieving consecutive big responses without reading the response hangs the client, see
            # https://github.com/aio-libs/aiohttp/issues/2217
            for response in responses:
                await response.read()
            all_responses.extend(responses := await super()._get_source_responses(*next_urls))
        return all_responses

    def _basic_auth_credentials(self) -> tuple[str, str] | None:
        """Override to return None, as the private token is passed as header."""
        return None

    def _headers(self) -> dict[str, str]:
        """Extend to add the private token, if any, to the headers."""
        headers = super()._headers()
        if private_token := self._parameter("private_token"):
            headers["Private-Token"] = str(private_token)
        return headers

    async def _next_urls(self, responses: SourceResponses) -> list[URL]:
        """Return the next (pagination) links from the responses."""
        return [URL(next_url) for response in responses if (next_url := response.links.get("next", {}).get("url"))]


class GitLabProjectBase(GitLabBase, ABC):
    """Base class for GitLab collectors for a specific project."""

    async def _gitlab_api_url(self, api: str) -> URL:
        """Return a GitLab API url for a project, if present in the parameters."""
        url = await super()._api_url()
        project = self._parameter("project", quote=True)
        api_url = URL(f"{url}/api/v4/projects/{project}" + (f"/{api}" if api else ""))
        return add_query(api_url, "per_page=100")


class GitLabJobsBase(GitLabProjectBase):
    """Base class for GitLab job collectors."""

    async def _api_url(self) -> URL:
        """Override to return the jobs API."""
        return await self._gitlab_api_url("jobs")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the jobs landing page."""
        return URL(f"{await super()._landing_url(responses)}/{self._parameter('project')}/-/jobs")

    async def _next_urls(self, responses: SourceResponses) -> list[URL]:
        """Return the next (pagination) links from the responses as long as we're within lookback days."""
        # Note: the GitLab documentation (https://docs.gitlab.com/ee/api/jobs.html#list-project-jobs) says:
        # "Jobs are sorted in descending order of their IDs." The API has no query parameters to sort jobs by date
        # created or by date run, so we're going to assume that descending order of IDs is roughly equal to descending
        # order of date created and date run. As soon as all jobs on a page have a build date that is outside the
        # lookback period we stop the pagination.
        lookback_dt = self._lookback_datetime()
        for response in responses:
            for job in await response.json():
                if self._build_datetime(job) >= lookback_dt:
                    return await super()._next_urls(responses)
        return []

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the jobs from the responses."""
        return Entities(
            [
                Entity(
                    branch=job["ref"],
                    build_date=str(self._build_datetime(job).date()),
                    build_datetime=self._build_datetime(job),
                    build_result=job["status"],
                    key=job["id"],
                    name=job["name"],
                    stage=job["stage"],
                    url=job["web_url"],
                )
                for job in await self._jobs(responses)
            ],
        )

    @staticmethod
    async def _jobs(responses: SourceResponses) -> list[Job]:
        """Return the jobs to count."""

        def newer(job1: Job, job2: Job) -> Job:
            """Return the newer of the two jobs."""
            return job1 if job1["created_at"] > job2["created_at"] else job2

        jobs: dict[tuple[str, str, str], Job] = {}
        for response in responses:
            for job in await response.json():
                key = job["name"], job["stage"], job["ref"]
                jobs[key] = newer(job, jobs.get(key, job))
        return list(jobs.values())

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to count the job."""
        jobs_to_include = self._parameter("jobs_to_include")
        refs_to_include = self._parameter("refs_to_include")
        return (
            (match_string_or_regular_expression(entity["name"], jobs_to_include) if jobs_to_include else True)
            and (match_string_or_regular_expression(entity["branch"], refs_to_include) if refs_to_include else True)
            and not match_string_or_regular_expression(entity["name"], self._parameter("jobs_to_ignore"))
            and not match_string_or_regular_expression(entity["branch"], self._parameter("refs_to_ignore"))
            and entity["build_datetime"] >= self._lookback_datetime()
        )

    @staticmethod
    def _build_datetime(job: Job) -> datetime:
        """Return the build date of the job."""
        return parse_datetime(job.get("finished_at") or job["created_at"])

    def _lookback_datetime(self) -> datetime:
        """Return the lookback cut-off date."""
        return now() - timedelta(days=int(cast(str, self._parameter("lookback_days"))))


@dataclass
class Pipeline:
    """GitLab pipeline JSON. See https://docs.gitlab.com/ee/api/pipelines.html."""

    id: int
    project_id: int
    ref: str
    status: str
    source: str
    created_at: str
    updated_at: str
    web_url: str
    started_at: str | None = None
    finished_at: str | None = None
    duration: int | None = None  # Seconds

    def __init__(self, **kwargs) -> None:
        """Override to ignore unknown fields so the caller does not need to weed the GitLab pipeline JSON."""
        field_names = [field.name for field in fields(self)]
        for key, value in kwargs.items():
            if key in field_names:
                setattr(self, key, value)

    @property
    def start(self) -> datetime:
        """Return the pipeline start time.

        The started_at field may be empty, be prepared. See https://gitlab.com/gitlab-org/gitlab/-/issues/210353.
        """
        return parse_datetime(self.started_at or self.created_at)

    @property
    def end(self) -> datetime:
        """Return the pipeline end time.

        The finished_at field may empty if the pipeline hasn't finished yet. Use the current time as fallback.
        """
        return parse_datetime(self.finished_at) if self.finished_at else datetime.now(tz=tzutc())

    @property
    def datetime(self) -> datetime:
        """Return the datetime of the pipeline."""
        return parse_datetime(self.updated_at or self.created_at)

    @property
    def pipeline_duration(self) -> timedelta:
        """Return the duration of the pipeline."""
        return self.end - self.start if self.duration is None else timedelta(seconds=self.duration)


class GitLabPipelineBase(GitLabProjectBase):
    """Base class for GitLab pipeline collectors."""

    async def _api_url(self) -> URL:
        """Override to return the pipeline API."""
        lookback_date = (now() - timedelta(days=int(cast(str, self._parameter("lookback_days_pipelines"))))).date()
        return await self._gitlab_api_url(f"pipelines?updated_after={lookback_date}")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Override to return a landing URL for the first pipeline."""
        pipelines = await self._pipelines(responses)
        return URL(pipelines[0].web_url)

    async def _pipelines(self, responses: SourceResponses) -> list[Pipeline]:
        """Get the pipelines from the responses."""
        pipelines = []
        try:
            for response in responses:
                json = await response.json()
                # The GitLab pipelines endpoint returns a list or, if a pipeline id is passed, one pipeline. Harmonize:
                json_list = json if isinstance(json, list) else [json]
                pipelines.extend([Pipeline(**pipeline) for pipeline in json_list])
        except StopAsyncIteration:
            pass
        if pipelines := [pipeline for pipeline in pipelines if self._include_pipeline(pipeline)]:
            return pipelines
        error_message = "No pipelines found within the lookback period"
        raise CollectorError(error_message)

    def _include_pipeline(self, pipeline: Pipeline) -> bool:
        """Return whether this pipeline should be considered."""
        branches = self._parameter("branches")
        matches_branches = match_string_or_regular_expression(pipeline.ref, branches) if branches else True
        matches_status = pipeline.status in self._parameter("pipeline_statuses_to_include")
        matches_source = pipeline.source in self._parameter("pipeline_triggers_to_include")
        return matches_branches and matches_status and matches_source
