"""Report model class."""

from shared.model.report import Report as SharedReport

from .issue_tracker import IssueParameters, IssueTracker, IssueTrackerCredentials


class Report(SharedReport):
    """Subclass the shared report class to add methods specific for the API-server."""

    def issue_tracker(self) -> IssueTracker:
        """Return the issue tracker of the report."""
        issue_tracker_data = self.get("issue_tracker", {})
        parameters = issue_tracker_data.get("parameters", {})
        url = parameters.get("url", "")
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
        return IssueTracker(url, issue_parameters, credentials)

    def desired_response_time(self, status: str) -> int:
        """Return the desired response time for the metric status."""
        # Note that the frontend also has these constant, in src/defaults.js.
        defaults = {
            "debt_target_met": 60,
            "near_target_met": 21,
            "target_not_met": 7,
            "unknown": 3,
        }
        default = defaults.get(status, defaults["unknown"])
        return int(self.get("desired_response_times", {}).get(status, default))

    def desired_measurement_entity_response_time(self, status: str) -> int | None:
        """Return the desired response time for the measurement entity status."""
        defaults = {
            "confirmed": 180,
            "false_positive": 180,
            "wont_fix": 190,
            "fixed": 7,
        }
        default = defaults.get(status)
        return int(self.get("desired_response_times", {}).get(status, default)) if status in defaults else None
