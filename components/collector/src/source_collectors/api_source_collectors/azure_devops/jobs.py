"""Azure Devops Server jobs/pipelines collectors."""

from datetime import datetime
from typing import cast

from dateutil.parser import parse

from base_collectors import SourceCollector
from collector_utilities.functions import days_ago, match_string_or_regular_expression
from collector_utilities.type import URL, Job
from source_model import Entity, SourceMeasurement, SourceResponses


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
