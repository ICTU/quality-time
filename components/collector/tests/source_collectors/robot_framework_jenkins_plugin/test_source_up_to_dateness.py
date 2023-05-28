"""Unit tests for the Robot Framework Jenkins plugin source up-to-dateness collector."""

from tests.source_collectors.jenkins_plugin_test_case import JenkinsPluginSourceUpToDatenessMixin

from .base import RobotFrameworkJenkinsPluginTestCase


class RobotFrameworkJenkinsPluginSourceUpToDatenessTest(
    JenkinsPluginSourceUpToDatenessMixin,
    RobotFrameworkJenkinsPluginTestCase,
):
    """Unit tests for the Robot Framework Jenkins plugin source up-to-dateness collector."""
