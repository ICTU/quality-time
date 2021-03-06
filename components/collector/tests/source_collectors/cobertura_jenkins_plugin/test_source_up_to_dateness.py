"""Unit tests for the Cobertura Jenkins plugin source up-to-dateness collector."""

from ..jenkins_plugin_test_case import JenkinsPluginSourceUpToDatenessMixin

from .base import CoberturaJenkinsPluginTestCase


class CoberturaJenkinsPluginSourceUpToDatenessTest(  # skipcq: PTC-W0046
    JenkinsPluginSourceUpToDatenessMixin, CoberturaJenkinsPluginTestCase
):
    """Unit tests for the Cobertura Jenkins plugin source up-to-dateness collector."""
