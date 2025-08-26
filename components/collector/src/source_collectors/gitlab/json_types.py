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

    We don't use the pipeline details to determine the pipeline duration, but simply subtract the update_at and
    created_at timestamps. Reason is that GitLab itself is pretty unclear about what exactly the pipeline duration is.
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
    updated_at: str = ""
    schedule_description: str = ""  # Pipeline schedule description for scheduled pipelines

    @property
    def start(self) -> datetime:
        """Return the pipeline start time."""
        return parse_datetime(self.created_at)

    @property
    def end(self) -> datetime:
        """Return the pipeline end time."""
        return parse_datetime(self.updated_at) if self.updated_at else datetime.now(tz=tzutc())

    @property
    def datetime(self) -> datetime:
        """Return the datetime of the pipeline."""
        return parse_datetime(self.updated_at or self.created_at)

    @property
    def duration(self) -> timedelta:
        """Return the duration of the pipeline."""
        return self.end - self.start


@dataclass
class PipelineSchedule(GitLabJSON):
    """Dataclass for GitLab pipeline schedule."""

    id: int
    description: str
