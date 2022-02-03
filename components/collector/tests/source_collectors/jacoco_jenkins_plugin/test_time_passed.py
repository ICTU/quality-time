"""Unit tests for the JaCoCo Jenkins plugin time passed collector."""

from ..jenkins_plugin_test_case import JenkinsPluginTimePassedMixin

from .base import JaCoCoJenkinsPluginTestCase


class JaCoCoJenkinsPluginTimePassedTest(JenkinsPluginTimePassedMixin, JaCoCoJenkinsPluginTestCase):  # skipcq: PTC-W0046
    """Unit tests for the JaCoCo Jenkins plugin time passed collector."""
