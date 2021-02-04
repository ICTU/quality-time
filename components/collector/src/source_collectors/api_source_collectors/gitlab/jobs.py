"""GitLab jobs collectors."""

from typing import List, Sequence, Set, Tuple, cast

from dateutil.parser import parse

from collector_utilities.functions import days_ago, match_string_or_regular_expression
from collector_utilities.type import URL, Job
from source_model import Entity, SourceMeasurement, SourceResponses

from .base import GitLabBase


class GitLabJobsBase(GitLabBase):
    """Base class for GitLab job collectors."""

    async def _api_url(self) -> URL:
        """Override to return the jobs API."""
        return await self._gitlab_api_url("jobs")

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the jobs from the responses."""
        jobs = await self.__jobs(responses)
        entities = [
            Entity(
                key=job["id"],
                name=job["name"],
                url=job["web_url"],
                build_status=job["status"],
                branch=job["ref"],
                stage=job["stage"],
                build_date=str(parse(job["created_at"]).date()),
            )
            for job in jobs
        ]
        return SourceMeasurement(entities=entities)

    async def __jobs(self, responses: SourceResponses) -> Sequence[Job]:
        """Return the jobs to count."""
        jobs: List[Job] = []
        jobs_seen: Set[Tuple[str, str, str]] = set()
        for response in responses:
            for job in await response.json():
                job_fingerprint = job["name"], job["stage"], job["ref"]
                if job_fingerprint in jobs_seen:
                    continue
                jobs_seen.add(job_fingerprint)
                if self._count_job(job):
                    jobs.append(job)
        return jobs

    def _count_job(self, job: Job) -> bool:
        """Return whether to count the job."""
        return not match_string_or_regular_expression(
            job["name"], self._parameter("jobs_to_ignore")
        ) and not match_string_or_regular_expression(job["ref"], self._parameter("refs_to_ignore"))


class GitLabFailedJobs(GitLabJobsBase):
    """Collector class to get failed job counts from GitLab."""

    async def _api_url(self) -> URL:
        """Extend to return only failed jobs."""
        return URL(str(await super()._api_url()) + "&scope=failed")

    def _count_job(self, job: Job) -> bool:
        """Return whether the job has failed."""
        failure_types = list(self._parameter("failure_type"))
        return super()._count_job(job) and job["status"] in failure_types


class GitLabUnusedJobs(GitLabJobsBase):
    """Collector class to get unused job counts from GitLab."""

    def _count_job(self, job: Job) -> bool:
        """Return whether the job is unused."""
        max_days = int(cast(str, self._parameter("inactive_job_days")))
        return super()._count_job(job) and days_ago(parse(job["created_at"])) > max_days
