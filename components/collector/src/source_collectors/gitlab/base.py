"""GitLab collector base classes."""

from abc import ABC
from collections import defaultdict
from datetime import datetime, timedelta
from operator import itemgetter
from typing import cast

from shared.utils.date_time import now

from base_collectors import LinkPaginationSourceCollector, TokenAuthenticationSourceCollector
from collector_utilities.date_time import parse_datetime
from collector_utilities.functions import add_query
from collector_utilities.type import URL
from model import Entities, Entity, SourceResponses

from .json_types import Job, Pipeline, PipelineSchedule


class GitLabBase(LinkPaginationSourceCollector, TokenAuthenticationSourceCollector, ABC):
    """Base class for GitLab collectors."""

    PAGE_SIZE = "per_page=100"
    AUTH_HEADER = "Private-Token"

    def _basic_auth_credentials(self) -> tuple[str, str] | None:
        """Override to return None, as the private token is passed as header."""
        return None


class GitLabProjectBase(GitLabBase, ABC):
    """Base class for GitLab collectors for a specific project."""

    async def _gitlab_api_url(self, api: str) -> URL:
        """Return a GitLab API url for a project, if present in the parameters."""
        url = await super()._api_url()
        project = self._parameter("project", quote=True)
        api_url = URL(f"{url}/api/v4/projects/{project}" + (f"/{api}" if api else ""))
        return add_query(api_url, self.PAGE_SIZE)


class GitLabJobsBase(GitLabProjectBase):
    """Base class for GitLab job collectors."""

    async def _api_url(self) -> URL:
        """Override to return the jobs API."""
        return await self._gitlab_api_url("jobs")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the jobs landing page."""
        return URL(f"{await super()._landing_url(responses)}/{self._parameter('project')}/-/jobs")

    async def _next_urls(self, responses: SourceResponses) -> list[URL]:
        """Return the next (pagination) links from the responses as long as we're within look-back days."""
        # Note: the GitLab documentation (https://docs.gitlab.com/ee/api/jobs.html#list-project-jobs) says:
        # "Jobs are sorted in descending order of their IDs." The API has no query parameters to sort jobs by date
        # created or by date run, so we're going to assume that descending order of IDs is roughly equal to descending
        # order of date created and date run. As soon as all jobs on a page have a build date that is outside the
        # look-back period we stop the pagination.
        lookback_dt = self._lookback_datetime()
        for response in responses:
            for job in await response.json():
                if self._build_datetime(job) >= lookback_dt:
                    return await super()._next_urls(responses)
        return []

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the jobs from the responses."""
        return Entities([self._create_entity(job) for job in await self._jobs(responses)])

    def _create_entity(self, job: Job) -> Entity:
        """Create an entity from a job."""
        return Entity(
            branch=job["ref"],
            build_date=str(self._build_datetime(job).date()),
            build_datetime=self._build_datetime(job),
            build_result=job["status"],
            key=job["id"],
            name=job["name"],
            stage=job["stage"],
            url=job["web_url"],
        )

    async def _jobs(self, responses: SourceResponses) -> list[Job]:
        """Return the jobs to count, that is, the most recent run of each job."""
        return [runs[0] for runs in (await self._job_runs(responses)).values()]

    @staticmethod
    async def _job_runs(responses: SourceResponses) -> dict[tuple[str, str, str], list[Job]]:
        """Return the runs of each job, most recent run first. Jobs are identified by name, stage, and ref."""
        job_runs: dict[tuple[str, str, str], list[Job]] = defaultdict(list)
        for response in responses:
            for job in await response.json():
                job_runs[(job["name"], job["stage"], job["ref"])].append(job)
        for runs in job_runs.values():
            runs.sort(key=itemgetter("created_at"), reverse=True)
        return job_runs

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to count the job."""
        return (
            self._matches_filter(entity["name"], "jobs_to_include", "jobs_to_ignore")
            and self._matches_filter(entity["branch"], "refs_to_include", "refs_to_ignore")
            and entity["build_datetime"] >= self._lookback_datetime()
        )

    @staticmethod
    def _build_datetime(job: Job) -> datetime:
        """Return the build date of the job."""
        return parse_datetime(job.get("finished_at") or job["created_at"])

    def _lookback_datetime(self) -> datetime:
        """Return the look-back cut-off date."""
        return now() - timedelta(days=int(cast(str, self._parameter("lookback_days"))))


class GitLabPipelineBase(GitLabProjectBase):
    """Base class for GitLab pipeline collectors."""

    async def _api_url(self) -> URL:
        """Override to return the pipeline API."""
        lookback_date = (now() - timedelta(days=int(cast(str, self._parameter("lookback_days_pipelines"))))).date()
        return await self._gitlab_api_url(f"pipelines?updated_after={lookback_date}")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Override to return a landing URL for the first pipeline, or the pipelines page if there are none."""
        pipelines = await self._pipelines(responses)
        return URL(pipelines[0].web_url) if pipelines else await self._project_pipelines_landing_url(responses)

    async def _project_pipelines_landing_url(self, responses: SourceResponses) -> URL:
        """Return the landing URL of the pipelines page of the project."""
        return URL(f"{await super()._landing_url(responses)}/{self._parameter('project')}/-/pipelines")

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to get pipeline schedule descriptions."""
        # Get the pipeline schedule descriptions so the user can filter scheduled pipelines by schedule description
        # The pipeline schedule descriptions is a mapping from pipeline ids to schedule descriptions
        self.pipeline_schedule_descriptions = await self._scheduled_pipeline_descriptions()
        return await super()._get_source_responses(*urls)

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Parse the entities from the responses."""
        return Entities([self._create_entity(pipeline) for pipeline in await self._pipelines(responses)])

    def _create_entity(self, pipeline: Pipeline) -> Entity:
        """Create an entity from a GitLab pipeline."""
        return Entity(
            key=str(pipeline.id),
            name=pipeline.name,
            ref=pipeline.ref,
            status=pipeline.status,
            trigger=pipeline.source,
            schedule=pipeline.schedule_description,
            created=pipeline.created_at,
            updated=pipeline.updated_at,
            url=pipeline.web_url,
        )

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether this entity should be considered."""
        return self._matches_selection_filters(entity) and self._matches_status_filter(entity)

    def _matches_selection_filters(self, entity: Entity) -> bool:
        """Return whether the entity matches the branch, schedule, and trigger filters."""
        matches_branches = self._matches_filter(entity["ref"], "branches")
        matches_schedule_description = self._matches_filter(entity["schedule"], "pipeline_schedules_to_include")
        matches_trigger = entity["trigger"] in self._parameter("pipeline_triggers_to_include")
        return matches_branches and matches_schedule_description and matches_trigger

    def _matches_status_filter(self, entity: Entity) -> bool:
        """Return whether the entity matches the pipeline status filter."""
        return entity["status"] in self._parameter("pipeline_statuses_to_include")

    async def _pipeline_details(self, pipeline_ids: list[str]) -> list[Pipeline]:
        """Get the details, such as the duration, of the pipelines with the specified ids, in the same order."""
        if not pipeline_ids:
            return []
        urls = [await self._gitlab_api_url(f"pipelines/{pipeline_id}") for pipeline_id in pipeline_ids]
        # Skip GitLabPipelineBase._get_source_responses() because the pipeline schedules have already been retrieved
        responses = await super()._get_source_responses(*urls)
        return [Pipeline.from_json(**await response.json()) for response in responses]

    async def _pipelines(self, responses: SourceResponses) -> list[Pipeline]:
        """Get the pipelines from the responses."""
        pipelines = []
        for response in responses:
            for pipeline_json in await response.json():
                schedule_description = self.pipeline_schedule_descriptions.get(pipeline_json["id"], "")
                pipeline_json["schedule_description"] = schedule_description
                pipelines.append(Pipeline.from_json(**pipeline_json))
        return pipelines

    async def _scheduled_pipeline_descriptions(self) -> dict[int, str]:
        """Get the scheduled pipelines. Returns a mapping of scheduled pipeline IDs to their descriptions."""
        scheduled_pipeline_descriptions = {}
        for schedule in await self._pipeline_schedules():
            scheduled_pipelines_api = await self._gitlab_api_url(f"pipeline_schedules/{schedule.id}/pipelines")
            for response in await super()._get_source_responses(scheduled_pipelines_api):
                for scheduled_pipeline in await response.json():
                    scheduled_pipeline_descriptions[scheduled_pipeline["id"]] = schedule.description
        return scheduled_pipeline_descriptions

    async def _pipeline_schedules(self) -> list[PipelineSchedule]:
        """Get the pipeline schedules."""
        pipeline_schedules = []
        for response in await super()._get_source_responses(await self._gitlab_api_url("pipeline_schedules")):
            pipeline_schedules.extend([PipelineSchedule.from_json(**schedule) for schedule in await response.json()])
        return pipeline_schedules
