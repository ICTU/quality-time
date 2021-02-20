"""Robot Framework Jenkins plugin collector."""

from base_collectors import JenkinsPluginSourceUpToDatenessCollector

from .base import RobotFrameworkJenkinsPluginBaseClass


class RobotFrameworkJenkinsPluginSourceUpToDateness(
    RobotFrameworkJenkinsPluginBaseClass, JenkinsPluginSourceUpToDatenessCollector
):
    """Collector for the up-to-dateness of the Robot Framework Jenkins plugin coverage report."""
