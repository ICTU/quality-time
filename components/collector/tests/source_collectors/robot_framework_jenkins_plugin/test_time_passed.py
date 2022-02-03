"""Unit tests for the Robot Framework Jenkins plugin time passed collector."""

from ..jenkins_plugin_test_case import JenkinsPluginTimePassedMixin

from .base import RobotFrameworkJenkinsPluginTestCase


class RobotFrameworkJenkinsPluginTimePassedTest(  # skipcq: PTC-W0046
    JenkinsPluginTimePassedMixin, RobotFrameworkJenkinsPluginTestCase
):
    """Unit tests for the Robot Framework Jenkins plugin time passed collector."""
