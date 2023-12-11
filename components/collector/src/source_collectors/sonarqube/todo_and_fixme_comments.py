"""SonarQube todo and fixme comments collector."""

from .violations import SonarQubeViolations


class SonarQubeTodoAndFixmeComments(SonarQubeViolations):
    """SonarQube todo and fixme comments collector."""

    rules_configuration = "todo_and_fixme_comment_rules"
