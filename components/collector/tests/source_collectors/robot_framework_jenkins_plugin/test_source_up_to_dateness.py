"""Unit tests for the Robot Framework Jenkins plugin source up-to-dateness collector."""

from ..jenkins_plugin_test_case import JenkinsPluginSourceUpToDatenessMixin

from .base import RobotFrameworkJenkinsPluginTestCase


class RobotFrameworkJenkinsPluginSourceUpToDatenessTest(  # skipcq: PTC-W0046
    JenkinsPluginSourceUpToDatenessMixin, RobotFrameworkJenkinsPluginTestCase
):
    """Unit tests for the Robot Framework Jenkins plugin source up-to-dateness collector."""
