"""Base classes for OWASP Dependency Check collectors."""

from abc import ABC

from base_collectors import XMLFileSourceCollector


class OWASPDependencyCheckBase(XMLFileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for OWASP Dependency Check collectors."""

    allowed_root_tags = [
        f"{{https://jeremylong.github.io/DependencyCheck/dependency-check.{version}.xsd}}analysis"
        for version in ("2.0", "2.1", "2.2", "2.3", "2.4", "2.5")
    ]
