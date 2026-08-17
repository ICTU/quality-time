"""GitLab JSON types."""

from dataclasses import dataclass, fields
from datetime import datetime, timedelta
from typing import Any, Self

from dateutil.tz import tzutc

from collector_utilities.date_time import parse_datetime

type Job = dict[str, Any]


@dataclass
class GitLabJSON:
    """Base class for GitLab response JSON."""

    @classmethod
    def from_json(cls, **kwargs) -> Self:
        """Override to ignore unknown fields so the caller does not need to weed the GitLab JSON."""
        field_names = [field.name for field in fields(cls)]
        return cls(**{key: value for key, value in kwargs.items() if key in field_names})


@dataclass
class Pipeline(GitLabJSON):
    """GitLab pipeline JSON. See https://docs.gitlab.com/ee/api/pipelines.html.

    To determine the bruto duration of a pipeline, we don't get the duration reported by GitLab, but simply subtract
    the updated_at and created_at timestamps. Reason is that the API to list pipelines of a project does not return
    the duration.Getting the duration requires  a call to the API to get one pipelines for each pipeline.

    Note that GitLab does not report a duration for pipelines that have not finished.

    Also note that GitLab itself is pretty unclear about what exactly the pipeline duration is.
    See https://gitlab.com/gitlab-org/gitlab/-/issues/19594.
    """

    id: int
    project_id: int
    name: str
    ref: str
    status: str
    source: str
    created_at: str
    web_url: str
    duration: int | None = None
    updated_at: str = ""
    schedule_description: str = ""  # Pipeline schedule description for scheduled pipelines

    @property
    def datetime(self) -> datetime:  # ty: ignore[invalid-type-form]
        """Return the datetime of the pipeline."""
        return parse_datetime(self.updated_at or self.created_at)

    @property
    def bruto_duration(self) -> timedelta:
        """Return the bruto duration of the pipeline, meaning the duration including idle time."""
        start = parse_datetime(self.created_at)
        end = parse_datetime(self.updated_at) if self.updated_at else datetime.now(tz=tzutc())
        return end - start

    @property
    def netto_duration(self) -> timedelta:
        """Return the netto duration of the pipeline, meaning the duration excluding idle time."""
        return timedelta(seconds=self.duration or 0)


@dataclass
class PipelineSchedule(GitLabJSON):
    """Dataclass for GitLab pipeline schedule."""

    id: int
    description: str
