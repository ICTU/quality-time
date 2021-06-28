"""Data model unit tests."""

from unittest.mock import patch

from data.meta.data_model import DataModel

from .base import MetaModelTestCase


class DataModelTest(MetaModelTestCase):
    """Data model unit tests."""

    MODEL = DataModel
    DESCRIPTION = "Description."
    SCALES = dict(count=dict(name="Count", description="The count scale."))
    METRICS = dict(metric=dict(name="Metric", description="Description.", scales=["count"], sources=["source"]))

    @classmethod
    def source(cls, **kwargs):
        """Create a source fixture."""
        parameters = kwargs.pop("parameters", {})
        name = kwargs.pop("name", "Source")
        return dict(name=name, description="Source.", url="https://example.org", parameters=parameters, **kwargs)

    def test_invalid_scales(self):
        """Test that invalid scales throw an error."""
        model_kwargs = dict(
            scales=self.SCALES,
            metrics=dict(
                metric=dict(name="Metric", description=self.DESCRIPTION, scales=["invalid"], sources=["source"])
            ),
        )
        self.check_validation_error("Metric 'Metric' has invalid scales {'invalid'}", **model_kwargs)

    def test_unused_scales(self):
        """Test that unused scales throw an error."""
        model_kwargs = dict(scales=dict(count=dict(name="Count", description=self.DESCRIPTION)), metrics={})
        self.check_validation_error("Unused scales {'count'}", **model_kwargs)

    @patch("pathlib.Path")
    def test_source_parameters(self, path_class):
        """Test that the sources have at least one parameter for each metric supported by the source."""
        logo_path = path_class.return_value
        logo_path.parent = logo_path
        logo_path.__truediv__.return_value = logo_path
        logo_path.exists.return_value = True
        model_kwargs = dict(scales=self.SCALES, metrics=self.METRICS, sources=dict(source=self.source()))
        self.check_validation_error("No parameters for metric metric in source source", **model_kwargs)

    @patch("pathlib.Path")
    def test_source_parameters_list_valid_metric(self, path_class):
        """Test that the metrics listed by the source parameters are metrics that list the source."""
        model_kwargs = dict(
            scales=self.SCALES,
            metrics=self.METRICS,
            sources=dict(
                source=self.source(
                    parameters=dict(parameter=dict(name="parameter", type="string", metrics=["metric"]))
                ),
                other_source=self.source(
                    parameters=dict(parameter=dict(name="parameter", type="string", metrics=["metric"]))
                ),
            ),
        )
        self.check_validation_error(
            "Parameter parameter of source other_source lists metric metric as metric needing this parameter, "
            "but that metric doesn't list other_source as allowed source",
            **model_kwargs
        )
        path_class.assert_called_once()

    @patch("pathlib.Path")
    def test_configuration_refers_to_existing_metric(self, path_class):
        """Test that source configurations refer to metrics that exist."""
        model_kwargs = dict(
            scales={},
            metrics={},
            sources=dict(
                source=self.source(configuration=dict(config=dict(name="Config", value=["value"], metrics=["metric"])))
            ),
        )
        self.check_validation_error(
            "Configuration config of source source refers to non-existing metric metric", **model_kwargs
        )
        path_class.assert_called_once()

    @patch("pathlib.Path")
    def test_configuration_refers_to_metric_that_refers_to_source(self, path_class):
        """Test that source configurations refer to metrics that list the source as supported source."""
        model_kwargs = dict(
            scales=self.SCALES,
            metrics=self.METRICS,
            sources=dict(
                source=self.source(
                    parameters=dict(parameter=dict(name="parameter", type="string", metrics=["metric"]))
                ),
                invalid_source=self.source(
                    configuration=dict(config=dict(name="Config", value=["value"], metrics=["metric"]))
                ),
            ),
        )
        self.check_validation_error(
            "Configuration config of source invalid_source refers to metric metric, "
            "but metric doesn't list invalid_source as source",
            **model_kwargs
        )
        path_class.assert_called_once()

    @patch("pathlib.Path")
    def test_metrics_belong_to_at_least_one_subject(self, path_class):
        """Test that metrics belong to at least one subject."""
        model_kwargs = dict(
            scales=self.SCALES,
            metrics=self.METRICS,
            sources=dict(
                source=self.source(configuration=dict(config=dict(name="Config", value=["value"], metrics=["metric"])))
            ),
            subjects={},
        )
        self.check_validation_error("Metric metric is not listed in any subject", **model_kwargs)
        path_class.assert_called_once()

    @patch("pathlib.Path")
    def test_quality_time_lists_all_metric_types(self, path_class):
        """Test that Quality-time lists all metric types as possible values for its metric_type parameter."""
        model_kwargs = dict(
            scales=self.SCALES,
            metrics=dict(
                metric=dict(
                    name="Metric",
                    description=self.DESCRIPTION,
                    scales=["count"],
                    default_source="source",
                    sources=["quality_time", "source"],
                )
            ),
            sources=dict(
                source=self.source(
                    parameters=dict(parameter=dict(name="parameter", type="string", metrics=["metric"]))
                ),
                quality_time=self.source(
                    name="Quality-time",
                    parameters=dict(
                        metric_type=dict(
                            name="Metric type",
                            type="multiple_choice",
                            placeholder="all",
                            default_value=[],
                            values=["Metric", "Other metric"],
                            metrics=["metric"],
                        ),
                        source_type=dict(
                            name="Source type",
                            type="multiple_choice",
                            placeholder="all",
                            default_value=[],
                            values=["Quality-time", "Source"],
                            metrics=["metric"],
                        ),
                    ),
                ),
            ),
            subjects={},
        )
        self.check_validation_error(
            "Parameter metric_type of source quality_time doesn't list all metric types", **model_kwargs
        )
        path_class.assert_called_once()
