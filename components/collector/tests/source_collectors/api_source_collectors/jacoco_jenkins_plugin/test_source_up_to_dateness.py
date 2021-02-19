"""Unit tests for the JaCoCo Jenkins plugin source up-to-dateness collector."""

from ...source_collector_test_case import SourceCollectorTestCase
from ..jenkins_plugin_test_case import JenkinsPluginSourceUpToDatenessMixin


class JaCoCoJenkinsPluginSourceUpToDatenessTest(JenkinsPluginSourceUpToDatenessMixin, SourceCollectorTestCase):
    """Unit tests for the JaCoCo Jenkins plugin source up-to-dateness collector."""

    SOURCE_TYPE = "jacoco_jenkins_plugin"
