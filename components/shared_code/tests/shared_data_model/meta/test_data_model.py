"""Data model unit tests."""

from typing import ClassVar
from unittest.mock import Mock, patch

from pydantic import HttpUrl

from shared_data_model.meta.data_model import DataModel

from .base import MetaModelTestCase


class DataModelTest(MetaModelTestCase):
    """Data model unit tests."""

    MODEL = DataModel
    PARAMETERS: ClassVar[dict] = {"parameter": {"name": "parameter", "type": "string", "metrics": ["metric"]}}
    CONFIGURATION: ClassVar[dict] = {"config": {"name": "Config", "value": ["value"], "metrics": ["metric"]}}

    def setUp(self) -> None:
        """Set up the default model kwargs."""
        self.model_kwargs = {
            "scales": {},
            "metrics": {},
            "sources": {},
            "subjects": {},
        }

    @classmethod
    def scale(cls, **kwargs) -> dict[str, str | dict]:
        """Create a scale fixture."""
        return {"name": "Count", "description": "The count scale."} | kwargs

    @classmethod
    def source(cls, **kwargs) -> dict[str, str | dict]:
        """Create a source fixture."""
        url = HttpUrl("https://example.org")
        return {"name": "Source", "description": "Source.", "url": url, "parameters": {}} | kwargs

    @classmethod
    def metric(cls, **kwargs) -> dict[str, str | list[str]]:
        """Create a metric fixture."""
        return {"name": "Metric", "description": "Description.", "scales": ["count"], "sources": ["source"]} | kwargs

    @classmethod
    def other_metric(cls) -> dict[str, str | list[str]]:
        """Create another metric fixture."""
        return cls.metric(name="Other metric", sources=["quality_time"])

    @classmethod
    def quality_time(cls, **kwargs) -> dict[str, str | dict]:
        """Create a Quality-time source."""
        return cls.source(
            name="Quality-time",
            parameters={
                "metric_type": {
                    "name": "Metric type",
                    "type": "multiple_choice",
                    "placeholder": "all",
                    "default_value": [],
                    "values": ["Metric", "Other metric"],
                    "metrics": kwargs.get("metric_type_metrics") or ["metric", "other_metric"],
                },
                "source_type": {
                    "name": "Source type",
                    "type": "multiple_choice",
                    "placeholder": "all",
                    "default_value": [],
                    "values": kwargs.get("source_type_values") or ["Quality-time", "Source"],
                    "metrics": ["metric"],
                },
            },
        )

    @staticmethod
    def mock_path(path_class, exists: bool = True) -> Mock:
        """Return a mock path that does or does not exist."""
        path = path_class.return_value
        path.parent = path
        path.__truediv__.return_value = path
        path.exists.return_value = exists
        return path

    def test_invalid_scales(self):
        """Test that invalid scales throw an error."""
        model_kwargs = self.model_kwargs | {
            "scales": {"count": self.scale()},
            "metrics": {"metric": self.metric(scales=["invalid"])},
        }
        self.check_validation_error("Metric 'Metric' has invalid scales {'invalid'}", **model_kwargs)

    def test_unused_scales(self):
        """Test that unused scales throw an error."""
        model_kwargs = self.model_kwargs | {"scales": {"count": self.scale()}}
        self.check_validation_error("Unused scales {'count'}", **model_kwargs)

    def test_source_urls(self):
        """Test that sources have a URL."""
        model_kwargs = self.model_kwargs | {"sources": {"source": self.source(url=None)}}
        self.check_validation_error("Source source has no URL", **model_kwargs)

    @patch("pathlib.Path")
    def test_missing_logo(self, path_class):
        """Test that a validation error occurs when a logo is missing."""
        model_kwargs = self.model_kwargs | {
            "scales": {"count": self.scale()},
            "metrics": {"metric": self.metric()},
            "sources": {"source": self.source()},
        }
        self.mock_path(path_class, exists=False)
        self.check_validation_error("No logo exists for source", **model_kwargs)

    @patch("pathlib.Path")
    def test_missing_source(self, path_class):
        """Test that a validation error occurs when a logo exists, but the source is missing."""
        model_kwargs = self.model_kwargs | {
            "scales": {"count": self.scale()},
            "metrics": {"metric": self.metric()},
            "sources": {"source": self.source()},
        }
        logo_path = self.mock_path(path_class)
        logo_path.glob.return_value = [logo_path]
        logo_path.stem = "non_existing_source"
        self.check_validation_error("No source exists for ", **model_kwargs)

    @patch("pathlib.Path")
    def test_source_parameters(self, path_class):
        """Test that the sources have at least one parameter for each metric supported by the source."""
        self.mock_path(path_class, exists=True)
        model_kwargs = self.model_kwargs | {
            "scales": {"count": self.scale()},
            "metrics": {"metric": self.metric()},
            "sources": {"source": self.source()},
        }
        self.check_validation_error("No parameters for metric metric in source source", **model_kwargs)

    @patch("pathlib.Path")
    def test_source_parameters_list_valid_metric(self, path_class):
        """Test that the metrics listed by the source parameters are metrics that list the source."""
        model_kwargs = self.model_kwargs | {
            "scales": {"count": self.scale()},
            "metrics": {"metric": self.metric()},
            "sources": {
                "source": self.source(parameters=self.PARAMETERS),
                "other_source": self.source(parameters=self.PARAMETERS),
            },
        }
        self.check_validation_error(
            "Parameter parameter of source other_source lists metric metric as metric needing this parameter, "
            "but that metric doesn't list other_source as allowed source",
            **model_kwargs,
        )
        path_class.assert_called_once()

    @patch("pathlib.Path")
    def test_configuration_refers_to_existing_metric(self, path_class):
        """Test that source configurations refer to metrics that exist."""
        model_kwargs = self.model_kwargs | {
            "sources": {"source": self.source(configuration=self.CONFIGURATION)},
        }
        self.check_validation_error(
            "Configuration config of source source refers to non-existing metric metric",
            **model_kwargs,
        )
        path_class.assert_called_once()

    @patch("pathlib.Path")
    def test_configuration_refers_to_metric_that_refers_to_source(self, path_class):
        """Test that source configurations refer to metrics that list the source as supported source."""
        model_kwargs = self.model_kwargs | {
            "scales": {"count": self.scale()},
            "metrics": {"metric": self.metric()},
            "sources": {
                "source": self.source(parameters=self.PARAMETERS),
                "invalid_source": self.source(configuration=self.CONFIGURATION),
            },
        }
        self.check_validation_error(
            "Configuration config of source invalid_source refers to metric metric, "
            "but metric doesn't list invalid_source as source",
            **model_kwargs,
        )
        path_class.assert_called_once()

    @patch("pathlib.Path")
    def test_metrics_belong_to_at_least_one_subject(self, path_class):
        """Test that metrics belong to at least one subject."""
        model_kwargs = self.model_kwargs | {
            "scales": {"count": self.scale()},
            "metrics": {
                "metric": self.metric(sources=["quality_time", "source"]),
                "other_metric": self.other_metric(),
            },
            "sources": {
                "source": self.source(parameters=self.PARAMETERS),
                "quality_time": self.quality_time(),
            },
        }
        self.check_validation_error("Metric metric is not listed in any subject", **model_kwargs)
        path_class.assert_called_once()

    @patch("pathlib.Path")
    def test_quality_time_lists_all_metric_types(self, path_class):
        """Test that Quality-time lists all metric types as possible values for its metric_type parameter."""
        model_kwargs = self.model_kwargs | {
            "scales": {"count": self.scale()},
            "metrics": {"metric": self.metric(sources=["quality_time", "source"])},
            "sources": {
                "source": self.source(parameters=self.PARAMETERS),
                "quality_time": self.quality_time(metric_type_metrics=["metric"]),
            },
        }
        self.check_validation_error(
            "Parameter metric_type of source quality_time doesn't list all metric types",
            **model_kwargs,
        )
        path_class.assert_called_once()

    @patch("pathlib.Path")
    def test_quality_time_lists_all_source_types(self, path_class):
        """Test that the Quality-time source lists all sources as possible values for its source type parameter."""
        model_kwargs = self.model_kwargs | {
            "scales": {"count": self.scale()},
            "metrics": {
                "metric": self.metric(sources=["quality_time", "source"]),
                "other_metric": self.other_metric(),
            },
            "sources": {
                "source": self.source(parameters=self.PARAMETERS),
                "quality_time": self.quality_time(source_type_values=["Other source", "Source"]),
            },
        }
        self.check_validation_error(
            "Parameter source_type of source quality_time doesn't list source types: Quality-time",
            **model_kwargs,
        )
        path_class.assert_called_once()
