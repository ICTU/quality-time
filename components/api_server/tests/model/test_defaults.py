"""Unit tests for the model defaults."""

from model.defaults import default_metric_attributes, default_source_parameters, default_subject_attributes

from tests.base import DataModelTestCase


class DefaultAttributesTest(DataModelTestCase):
    """Test the default attributes."""

    def test_default_source_parameters(self):
        """Test that the default source parameters can be retrieved from the data model."""
        expected_parameters = {
            "landing_url": "",
            "password": "",
            "private_token": "",
            "severities": [],
            "url": "",
            "username": "",
        }
        self.assertEqual(expected_parameters, default_source_parameters("security_warnings", "snyk"))

    def test_default_metric_attributes(self):
        """Test that the default metric attributes can be retrieved from the data model."""
        self.assertEqual(
            {
                "name": None,
                "type": "dependencies",
                "accept_debt": False,
                "addition": "sum",
                "debt_target": None,
                "direction": None,
                "near_target": "10",
                "target": "0",
                "scale": "count",
                "sources": {},
                "tags": ["maintainability"],
                "unit": None,
            },
            default_metric_attributes("dependencies"),
        )

    def test_default_subject_attributes(self):
        """Test that the default subject attributes can be retrieved from the data model."""
        self.assertEqual(
            {
                "name": None,
                "description": "A custom software application or component.",
                "type": "software",
                "metrics": {},
            },
            default_subject_attributes("software"),
        )
