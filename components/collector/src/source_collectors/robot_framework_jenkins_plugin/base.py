"""Robot Framework Jenkins plugin collector base classes."""

from abc import ABC

from base_collectors import JenkinsPluginCollector


class RobotFrameworkJenkinsPluginBaseClass(JenkinsPluginCollector, ABC):  # skipcq: PYL-W0223
    """Base class for Robot Framework Jenkins plugin collectors."""

    plugin = "robot"
