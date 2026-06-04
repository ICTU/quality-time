"""Base classes for the model unit tests."""

from unittest.mock import Mock

from shared_test_code.base import DataModelTestCase


class DatabaseTestCase(DataModelTestCase):
    """Base class with a database fixture."""

    def setUp(self):
        """Extend to set of the data models database collection."""
        super().setUp()
        self.database = Mock()


class DatabaseWithDataModelTestCase(DatabaseTestCase):
    """Base class with a database fixture containing the data model."""

    def setUp(self):
        """Extend to set of the data models database collection."""
        super().setUp()
        self.database.datamodels.find_one.return_value = self.DATA_MODEL
