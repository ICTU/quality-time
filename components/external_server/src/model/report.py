"""Report model class."""

from shared.model.report import Report as SharedReport

from .issue_tracker import IssueParameters, IssueTracker, IssueTrackerCredentials


class Report(SharedReport):
    """Subclass the shared report class to add methods specific for the external server."""

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
            parameters.get("username", ""), parameters.get("password", ""), parameters.get("private_token", "")
        )
        return IssueTracker(url, issue_parameters, credentials)
