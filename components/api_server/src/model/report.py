"""Report model class."""

from datetime import timedelta

from shared.model.report import Report as SharedReport
from shared.utils.date_time import now

from .issue_tracker import IssueParameters, IssueTracker, IssueTrackerCredentials


class Report(SharedReport):
    """Subclass the shared report class to add methods specific for the API-server."""

    def issue_tracker(self) -> IssueTracker:
        """Return the issue tracker of the report."""
        issue_tracker_data = self.get("issue_tracker", {})
        parameters = issue_tracker_data.get("parameters", {})
        url = parameters.get("url", "")
        api_version = parameters.get("api_version", "v2")
        issue_parameters = IssueParameters(
            parameters.get("project_key", ""),
            parameters.get("issue_type", ""),
            parameters.get("issue_labels", []),
            parameters.get("epic_link", ""),
        )
        credentials = IssueTrackerCredentials(
            parameters.get("username", ""),
            parameters.get("password", ""),
            parameters.get("private_token", ""),
        )
        return IssueTracker(url, api_version, issue_parameters, credentials)

    def deadline(self, status: str) -> str | None:
        """Return the deadline for metrics or measurement entities with the given status."""
        desired_response_time = self._desired_response_time(status)
        return None if desired_response_time is None else str((now() + timedelta(days=desired_response_time)).date())

    def _desired_response_time(self, status: str) -> int | None:
        """Return the desired response time for the given status."""
        # Note that the frontend also has these constants, in src/defaults.js.
        defaults = {
            "debt_target_met": 60,
            "near_target_met": 21,
            "target_not_met": 7,
            "unknown": 3,
            "confirmed": 180,
            "false_positive": 180,
            "wont_fix": 180,
            "fixed": 7,
        }
        if status not in self.get("desired_response_times", {}):
            return defaults.get(status)
        try:
            return int(self["desired_response_times"][status])
        except (ValueError, TypeError):  # The desired response time can be empty, treat any non-integer as None
            return None
