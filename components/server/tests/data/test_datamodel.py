"""Unit tests for the data model."""

import json
import unittest


def setUpModule():  # pylint: disable=invalid-name
    """Read the data model once for all data model tests."""
    with open("src/data/datamodel.json") as data_model_json:
        DataModelTestCase.data_model = json.load(data_model_json)


class DataModelTestCase(unittest.TestCase):
    """Base class for data model unit tests."""

    data_model = dict()


class DataModelTest(DataModelTestCase):
    """Unit tests for the data model."""

    def test_top_level_keys(self):
        """Test that the top level keys are correct."""
        self.assertEqual({"metrics", "subjects", "sources", "scales"}, set(self.data_model.keys()))

    def test_metrics_have_sources(self):
        """Test that each metric has one or more sources."""
        for metric in self.data_model["metrics"].values():
            self.assertTrue(len(metric["sources"]) >= 1)

    def test_source_parameter_metrics(self):
        """Test that the metrics listed for source parameters are metrics supported by the source."""
        for source_id, source in self.data_model["sources"].items():
            for parameter_key, parameter_value in source["parameters"].items():
                for metric in parameter_value["metrics"]:
                    self.assertTrue(
                        source_id in self.data_model["metrics"][metric]["sources"],
                        f"Parameter '{parameter_key}' of source '{source_id}' lists metric '{metric}' as metric "
                        f"needing this parameter, but that metric doesn't list '{source_id}' as allowed source")

    def test_source_parameter_names(self):
        """Test that each source parameter has a name and short name."""
        for source_id, source in self.data_model["sources"].items():
            for parameter_key, parameter_value in source["parameters"].items():
                for field in ["name", "short_name"]:
                    error_message = f"Parameter '{parameter_key}' of source '{source_id}' has no {field}"
                    self.assertTrue(field in parameter_value, error_message)

    def test_source_parameters(self):
        """Test that the sources have at least one parameter for each metric supported by the source."""
        for metric_id, metric in self.data_model["metrics"].items():
            for source in metric["sources"]:
                # pylint: disable=superfluous-parens
                if not (parameters := self.data_model["sources"][source]["parameters"]):
                    continue
                parameter_metrics = []
                for parameter in parameters.values():
                    parameter_metrics.extend(parameter["metrics"])
                self.assertTrue(
                    metric_id in parameter_metrics, f"No parameters for metric '{metric_id}' in source '{source}'")

    def test_multiple_choice_parameters(self):
        """Test that multiple choice parameters have both a default value and a list of options."""
        for source in self.data_model["sources"].values():
            for parameter in source["parameters"].values():
                if parameter["type"].startswith("multiple_choice"):
                    self.assertTrue("default_value" in parameter)
                    self.assertEqual(list, type(parameter["default_value"]))
                    if parameter["type"] == "multiple_choice":
                        self.assertTrue("values" in parameter)

    def test_addition(self):
        """Test each metric had its addition defined correctly."""
        for metric in self.data_model["metrics"].values():
            self.assertTrue(metric["addition"] in ("max", "min", "sum"))

    def test_mandatory_parameters(self):
        """Test that each metric has a mandatory field with true or false value."""
        for source_id, source in self.data_model["sources"].items():
            for parameter_id, parameter_values in source["parameters"].items():
                self.assertTrue(
                    "mandatory" in parameter_values,
                    f"The parameter '{parameter_id}' of source '{source_id}' has no 'mandatory' field")
                self.assertTrue(
                    parameter_values["mandatory"] in (True, False),
                    f"The 'mandatory' field of parameter '{parameter_id}' of source '{source_id}' is neither "
                    "true nor false")

    def test_default_source(self):
        """Test that each metric has a default source, and that the default source is listed as possible source."""
        for metric in self.data_model["metrics"].values():
            self.assertTrue(metric["default_source"] in metric["sources"])

    def test_entity_attributes(self):
        """Test that entities have the required attributes."""
        for source_id, source in self.data_model["sources"].items():
            for entity_key, entity_value in source["entities"].items():
                self.assertTrue("name" in entity_value.keys())
                self.assertTrue("name_plural" in entity_value.keys(), f"No 'name_plural' in {source_id}.{entity_key}")

    def test_colors(self):
        """Test that the color values are correct."""
        for source_id, source in self.data_model["sources"].items():
            for entity_key, entity_value in source["entities"].items():
                for attribute in entity_value["attributes"]:
                    for color_value in attribute.get("color", {}).values():
                        self.assertTrue(
                            color_value in ("active", "error", "negative", "positive", "warning"),
                            f"Color {color_value} of {source_id}.{entity_key} is not correct")

    def test_metrics_belong_to_at_least_one_subject(self):
        """Test that each metric belongs to at least one subject."""
        for metric in self.data_model["metrics"]:
            for subject in self.data_model["subjects"].values():
                if metric in subject["metrics"]:
                    break
            else:  # pragma: nocover
                self.fail(f"Metric {metric} not listed in any subject.")

    def test_sources_with_landing_url(self):
        """Test that the the sources with landing url also have url."""
        for source in self.data_model["sources"]:
            if "landing_url" in self.data_model["sources"][source]["parameters"]:
                self.assertTrue(
                    "url" in self.data_model["sources"][source]["parameters"],
                    f"Source '{source}' has the 'landing_url' parameter, but not the 'url' parameter.")

    def test_metric_direction(self):
        """Test that all metrics have a valid direction."""
        for metric_uuid, metric in self.data_model["metrics"].items():
            direction = metric["direction"]
            self.assertTrue(direction in ("<", ">"), f"Metric {metric_uuid} has an invalid direction: {direction}")

    def test_metrics_have_scales(self):
        """Test that all metrics have one or more allowed scales and a default scale that's in the allowed scales."""
        scales = self.data_model["scales"].keys()
        for metric_id, metric in self.data_model["metrics"].items():
            allowed_scales = metric.get("scales", [])
            self.assertTrue(len(allowed_scales) > 0, f"Metric {metric} has no scales")
            for scale in allowed_scales:
                self.assertTrue(scale in scales, f"Metric scale {scale} not in collection of all scales")
            default_scale = metric["default_scale"]
            self.assertTrue(
                default_scale in allowed_scales,
                f"Default scale {default_scale} of metric {metric_id} not in allowed scales: {allowed_scales}")

    def test_all_scales_are_used(self):
        """Test that all scales are used at least once."""
        for scale in self.data_model["scales"].keys():
            for metric in self.data_model["metrics"].values():
                if scale in metric.get("scales", []):
                    break
            else:  # pragma: nocover
                self.fail(f"Scale {scale} not used for any metric.")

    def test_parameter_api_values(self):
        """Test that the api values are only used for single or multiple choice parameters and that the keys match with
        the possible regular values. The api values are the values used in the source."""
        for source_id, source in self.data_model["sources"].items():
            for parameter_key, parameter in source["parameters"].items():
                if "api_values" not in parameter:
                    continue
                self.assertTrue(
                    "values" in parameter,
                    f"Parameter {parameter_key} of source {source_id} has api values, but no values.")
                self.assertEqual(set(parameter["api_values"].keys()), set(parameter["values"]))

    def test_invalid_characters_in_names(self):
        """Test that we don't use dots in metric or source names since we want to be able to use the names as keys."""
        for source in self.data_model["sources"].values():
            self.assertFalse("." in source["name"])
        for metric in self.data_model["metrics"].values():
            self.assertFalse("." in metric["name"])

    def test_validate_on(self):
        """Test that the list of parameters to validate on are in fact parameters of the source."""
        for source in self.data_model["sources"].values():
            parameter_keys = source["parameters"].keys()
            for parameter_value in source["parameters"].values():
                for parameter_key in parameter_value.get("validate_on", []):
                    self.assertTrue(parameter_key in parameter_keys)


class DataModelSpecificSourcesTest(DataModelTestCase):
    """Unit tests for specific sources in the data model."""

    def test_quality_time_source_type_parameter(self):
        """Test that the source type parameter of the Quality-time source lists all source types."""
        all_source_names = set(source["name"] for source in self.data_model["sources"].values())
        quality_time_source_names = set(
            self.data_model["sources"]["quality_time"]["parameters"]["source_type"]["values"])
        self.assertEqual(all_source_names, quality_time_source_names)
        all_source_api_values = set(
            (source["name"], source_id) for source_id, source in self.data_model["sources"].items())
        quality_time_api_values = set(
            self.data_model["sources"]["quality_time"]["parameters"]["source_type"]["api_values"].items())
        self.assertEqual(all_source_api_values, quality_time_api_values)

    def test_quality_time_metric_type_parameter(self):
        """Test that the metric type parameter of the Quality-time source lists all metric types."""
        all_metric_names = set(metric["name"] for metric in self.data_model["metrics"].values())
        quality_time_metric_names = set(
            self.data_model["sources"]["quality_time"]["parameters"]["metric_type"]["values"])
        self.assertEqual(all_metric_names, quality_time_metric_names)
        all_metric_api_values = set(
            (metric["name"], metric_id) for metric_id, metric in self.data_model["metrics"].items())
        quality_time_api_values = set(
            self.data_model["sources"]["quality_time"]["parameters"]["metric_type"]["api_values"].items())
        self.assertEqual(all_metric_api_values, quality_time_api_values)
