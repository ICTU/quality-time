"""Unit tests for the Robot Framework Jenkins plugin source up-to-dateness collector."""

from ..jenkins_plugin_test_case import JenkinsPluginTestCase, JenkinsPluginSourceUpToDatenessMixin


class RobotFrameworkJenkinsPluginSourceUpToDatenessTest(JenkinsPluginSourceUpToDatenessMixin, JenkinsPluginTestCase):
    """Unit tests for the Robot Framework Jenkins plugin source up-to-dateness collector."""

    SOURCE_TYPE = "robot_framework_jenkins_plugin"
