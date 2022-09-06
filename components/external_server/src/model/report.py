"""Report model class."""

from shared.model.report import Report as SharedReport

from .issue_tracker import IssueTracker


class Report(SharedReport):
    """Subclass the shared report class to add methods specific for the external server."""

    def issue_tracker(self) -> IssueTracker:
        """Return the issue tracker of the report."""
        issue_tracker_data = self.get("issue_tracker", {})
        parameters = issue_tracker_data.get("parameters", {})
        url = parameters.get("url", "")
        project_key = parameters.get("project_key", "")
        issue_type = parameters.get("issue_type", "")
        issue_labels = parameters.get("issue_labels", [])
        username = parameters.get("username", "")
        password = parameters.get("password", "")
        private_token = parameters.get("private_token", "")
        return IssueTracker(url, project_key, issue_type, issue_labels, username, password, private_token)
