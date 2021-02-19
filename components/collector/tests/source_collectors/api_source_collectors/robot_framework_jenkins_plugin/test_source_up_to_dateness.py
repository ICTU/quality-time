"""Unit tests for the Robot Framework Jenkins plugin source up-to-dateness collector."""

from ...source_collector_test_case import SourceCollectorTestCase
from ..jenkins_plugin_test_case import JenkinsPluginSourceUpToDatenessMixin


class RobotFrameworkJenkinsPluginSourceUpToDatenessTest(JenkinsPluginSourceUpToDatenessMixin, SourceCollectorTestCase):
    """Unit tests for the Robot Framework Jenkins plugin source up-to-dateness collector."""

    SOURCE_TYPE = "robot_framework_jenkins_plugin"
