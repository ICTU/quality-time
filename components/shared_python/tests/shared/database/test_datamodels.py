"""Test the data models collection."""

import unittest
from unittest.mock import Mock

from shared.database.datamodels import (
    default_source_parameters,
    default_metric_attributes,
    latest_datamodel,
    default_subject_attributes,
)


class DataModelsTest(unittest.TestCase):
    """Unit tests for getting the data model from the data models collection."""

    def setUp(self) -> None:
        """Override to create a database fixture."""
        self.database = Mock()

    def test_default_source_parameters(self):
        """Test that the a default source parameter can get retrieved."""
        self.database.datamodels.find_one.return_value = dict(
            _id="id",
            sources=dict(
                test_source=dict(
                    parameters=dict(
                        test_parameter=dict(
                            default_value="value", metrics=["metric_type"]
                        ),
                        test_parameter_2=dict(
                            default_value="value_2", metrics=["some_other_metric"]
                        ),
                    )
                ),
                source_type=dict(
                    parameters=dict(
                        test_parameter_3=dict(
                            default_value="value_3", metrics=["metric_type"]
                        ),
                        test_parameter_4=dict(
                            default_value="value_4", metrics=["some_other_metric"]
                        ),
                    )
                ),
            ),
        )

        default_params = default_source_parameters(
            self.database, "metric_type", "test_source"
        )

        self.assertDictEqual(default_params, dict(test_parameter="value"))

    def test_default_metric_attributes(self):
        """Test that default metric attributes get retrieved."""
        self.database.datamodels.find_one.return_value = dict(
            _id="id",
            metrics=dict(
                metric_type=dict(
                    default_scale="test",
                    addition="test_addition",
                    target="test_target",
                    near_target="test_near_target",
                    tags=["tag", "tag-2"],
                ),
                metric_type_2=dict(
                    default_scale="test2",
                    addition="test_addition2",
                    target="test_target2",
                    near_target="test_near_target2",
                    tags=["tag", "tag-3"],
                ),
            ),
        )

        expected_dict = dict(
            type="metric_type",
            sources={},
            name=None,
            scale="test",
            unit=None,
            addition="test_addition",
            accept_debt=False,
            debt_target=None,
            direction=None,
            target="test_target",
            near_target="test_near_target",
            tags=["tag", "tag-2"],
        )
        self.assertDictEqual(default_metric_attributes(self.database), expected_dict)

        expected_dict = dict(
            type="metric_type_2",
            sources={},
            name=None,
            scale="test2",
            unit=None,
            addition="test_addition2",
            accept_debt=False,
            debt_target=None,
            direction=None,
            target="test_target2",
            near_target="test_near_target2",
            tags=["tag", "tag-3"],
        )
        self.assertDictEqual(
            default_metric_attributes(self.database, "metric_type_2"), expected_dict
        )

    def test_default_subject_attributes(self):
        """Test that default subject attributes get retrieved."""
        self.database.datamodels.find_one.return_value = dict(
            _id="id",
            subjects=dict(
                subject_type=dict(description="description"), subject_type_2={}
            ),
        )

        expected_dict = dict(
            type="subject_type", name=None, description="description", metrics={}
        )
        self.assertDictEqual(default_subject_attributes(self.database), expected_dict)

    def test_latest_data_model(self):
        """Test that the data model can be retrieved."""
        self.database.datamodels.find_one.return_value = data_model = dict(
            _id="id", metrics=dict(metric_type={})
        )
        self.assertEqual(data_model, latest_datamodel(self.database))

    def test_no_latest_data_model(self):
        """Test that retrieving a missing data model returns an empty dict."""
        self.database.datamodels.find_one.return_value = None
        self.assertEqual({}, latest_datamodel(self.database))
