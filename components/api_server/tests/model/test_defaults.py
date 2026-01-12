"""Unit tests for the model defaults."""

from model.defaults import default_metric_attributes, default_source_parameters, default_subject_attributes

from tests.base import DataModelTestCase


class DefaultAttributesTest(DataModelTestCase):
    """Test the default attributes."""

    def test_default_source_parameters(self):
        """Test that the default source parameters can be retrieved from the data model."""
        expected_parameters = {
            "landing_url": "",
            "password": "",  # nosec
            "private_token": "",  # nosec
            "severities": ["low", "medium", "high"],
            "url": "",
            "username": "",
        }
        self.assertEqual(expected_parameters, default_source_parameters("security_warnings", "snyk"))

    def test_default_metric_attributes(self):
        """Test that the default metric attributes can be retrieved from the data model."""
        self.assertEqual(
            {
                "name": None,
                "type": "software_version",
                "accept_debt": False,
                "debt_target": None,
                "direction": None,
                "evaluate_targets": False,
                "near_target": "0.9",
                "target": "1.0",
                "scale": "version_number",
                "sources": {},
                "tags": ["ci"],
                "unit": None,
                "unit_singular": None,
            },
            default_metric_attributes("software_version"),
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
