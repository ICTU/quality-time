"""Unit tests for the Cobertura Jenkins plugin source up-to-dateness collector."""

from ...source_collector_test_case import SourceCollectorTestCase
from ..jenkins_plugin_test_case import JenkinsPluginSourceUpToDatenessMixin


class CoberturaJenkinsPluginSourceUpToDatenessTest(JenkinsPluginSourceUpToDatenessMixin, SourceCollectorTestCase):
    """Unit tests for the Cobertura Jenkins plugin source up-to-dateness collector."""

    SOURCE_TYPE = "cobertura_jenkins_plugin"
