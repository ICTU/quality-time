"""Unit tests for the JaCoCo Jenkins plugin source up-to-dateness collector."""

from ..jenkins_plugin_test_case import JenkinsPluginSourceUpToDatenessMixin

from .base import JaCoCoJenkinsPluginTestCase


class JaCoCoJenkinsPluginSourceUpToDatenessTest(  # skipcq: PTC-W0046
    JenkinsPluginSourceUpToDatenessMixin, JaCoCoJenkinsPluginTestCase
):
    """Unit tests for the JaCoCo Jenkins plugin source up-to-dateness collector."""
