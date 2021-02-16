"""Cobertura Jenkins plugin coverage report source up-to-dateness collector."""

from base_collectors import JenkinsPluginSourceUpToDatenessCollector

from .base import CoberturaJenkinsPluginBaseClass


class CoberturaJenkinsPluginSourceUpToDateness(
    CoberturaJenkinsPluginBaseClass, JenkinsPluginSourceUpToDatenessCollector
):
    """Collector for the up to dateness of the Cobertura Jenkins plugin coverage report."""
