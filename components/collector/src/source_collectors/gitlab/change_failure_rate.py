"""GitLab change failure rate deploys collector."""

from .job_runs_within_time_period import GitLabJobRunsWithinTimePeriod


class GitLabChangeFailureRate(GitLabJobRunsWithinTimePeriod):
    """Collector to get change failure rate from GitLab."""
