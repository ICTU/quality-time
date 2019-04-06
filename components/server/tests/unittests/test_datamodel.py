"""Unit tests for the data model."""

import json
import unittest


class DataModelTest(unittest.TestCase):
    """Unit tests for the data model."""

    def setUp(self):
        with open("datamodel.json") as datamodel_json:
            self.datamodel = json.load(datamodel_json)

    def test_top_level_keys(self):
        """Test that the top level keys are correct."""
        self.assertEqual(set(["metrics", "subjects", "sources"]), set(self.datamodel.keys()))

    def test_metrics_have_sources(self):
        """Test that each metric has one or more sources."""
        for metric in self.datamodel["metrics"].values():
            self.assertTrue(len(metric["sources"]) >= 1)

    def test_source_parameter_metrics(self):
        """Test that the metrics listed for source parameters are metrics supported by the source."""
        for source_id, source in self.datamodel["sources"].items():
            for parameter in source["parameters"].values():
                for metric in parameter["metrics"]:
                    self.assertTrue(source_id in self.datamodel["metrics"][metric]["sources"])

    def test_metric_source_parameters(self):
        """Test that the sources have at least one parameter for each metric supported by the source."""
        for metric_id, metric in self.datamodel["metrics"].items():
            parameter_metrics = []
            for source in metric["sources"]:
                for parameter in self.datamodel["sources"][source]["parameters"].values():
                    parameter_metrics.extend(parameter["metrics"])
            self.assertTrue(metric_id in parameter_metrics)

    def test_multiple_choice_paramters(self):
        """Test that multiple choice parameters have both a default value and a list of options."""
        for source in self.datamodel["sources"].values():
            for parameter in source["parameters"].values():
                if parameter["type"] == "multiple_choice":
                    self.assertTrue("default_value" in parameter)
                    self.assertTrue("values" in parameter)
