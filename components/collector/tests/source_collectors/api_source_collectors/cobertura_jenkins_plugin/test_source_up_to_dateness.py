"""Unit tests for the Cobertura Jenkins plugin source up-to-dateness collector."""

from ..jenkins_plugin_test_case import JenkinsPluginTestCase, JenkinsPluginSourceUpToDatenessMixin


class CoberturaJenkinsPluginSourceUpToDatenessTest(JenkinsPluginSourceUpToDatenessMixin, JenkinsPluginTestCase):
    """Unit tests for the Cobertura Jenkins plugin source up-to-dateness collector."""

    SOURCE_TYPE = "cobertura_jenkins_plugin"
