"""Unit tests for the Anchore Jenkins plugin time passed collector."""

from ..jenkins_plugin_test_case import JenkinsPluginTimePassedMixin
from ..source_collector_test_case import SourceCollectorTestCase


class AnchoreJenkinsPluginTimePassedTest(JenkinsPluginTimePassedMixin, SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Unit tests for the Anchore Jenkins plugin time passed collector."""

    SOURCE_TYPE = "anchore_jenkins_plugin"
