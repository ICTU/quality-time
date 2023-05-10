"""Unit tests for the Anchore Jenkins plugin source up-to-dateness collector."""

from tests.source_collectors.jenkins_plugin_test_case import JenkinsPluginSourceUpToDatenessMixin
from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class AnchoreJenkinsPluginSourceUpToDatenessTest(JenkinsPluginSourceUpToDatenessMixin, SourceCollectorTestCase):
    """Unit tests for the Anchore Jenkins plugin source up-to-dateness collector."""

    SOURCE_TYPE = "anchore_jenkins_plugin"
