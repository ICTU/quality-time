"""Base classes for Robot Framework Jenkins plugin unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class RobotFrameworkJenkinsPluginTestCase(SourceCollectorTestCase):
    """Robot Framework JaCoCo Jenkins plugin coverage base class."""

    SOURCE_TYPE = "robot_framework_jenkins_plugin"
