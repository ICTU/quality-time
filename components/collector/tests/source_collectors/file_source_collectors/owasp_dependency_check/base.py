"""Base classes for OWASP dependency check collector unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class OWASPDependencyCheckTestCase(SourceCollectorTestCase):
    """Base class for OWASP dependency check collector unit tests."""

    SOURCE_TYPE = "owasp_dependency_check"

    def setUp(self):
        """Extend to set up test data."""
        super().setUp()
        self.file_name = "jquery.min.js"
        self.file_path = f"/home/jenkins/workspace/hackazon-owaspdep/hackazon/js/{self.file_name}"
