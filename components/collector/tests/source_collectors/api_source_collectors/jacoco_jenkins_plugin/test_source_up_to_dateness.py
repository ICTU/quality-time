"""Unit tests for the JaCoCo Jenkins plugin source up-to-dateness collector."""

from ..jenkins_plugin_test_case import JenkinsPluginTestCase, JenkinsPluginSourceUpToDatenessMixin


class JaCoCoJenkinsPluginSourceUpToDatenessTest(JenkinsPluginSourceUpToDatenessMixin, JenkinsPluginTestCase):
    """Unit tests for the JaCoCo Jenkins plugin source up-to-dateness collector."""

    SOURCE_TYPE = "jacoco_jenkins_plugin"
