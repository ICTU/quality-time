"""Data model model."""

from pydantic import BaseModel, validator  # pylint: disable=no-name-in-module

from .metric import Metrics
from .scale import Scales
from .source import Sources
from .subject import Subjects


class DataModel(BaseModel):  # pylint: disable=too-few-public-methods
    """Data model model."""

    scales: Scales
    metrics: Metrics
    sources: Sources
    subjects: Subjects

    @validator("metrics")
    def check_scales(cls, metrics, values):  # pylint: disable=no-self-argument,no-self-use
        """Check that the metric scales are valid scales."""
        scales = set(values["scales"].__root__.keys())
        used_scales = set()
        for metric in metrics.__root__.values():
            metric_scales = set(metric.scales)
            if not metric_scales <= scales:
                raise ValueError(f"Metric '{metric.name}' has invalid scales {metric_scales - scales}")
            used_scales |= metric_scales
        if scales - used_scales:
            raise ValueError(f"Unused scales {scales - used_scales}")
        return metrics

    @validator("sources")
    def check_sources(cls, sources, values):  # pylint: disable=no-self-argument,no-self-use
        """Check that the sources are valid."""
        cls.check_source_has_parameters_for_each_supported_metric(sources, values)
        cls.check_metric_supports_source(sources, values)
        cls.check_source_configurations(sources, values)
        cls.check_quality_time_metric_types(sources, values)
        return sources

    @classmethod
    def check_source_has_parameters_for_each_supported_metric(cls, sources, values):
        """Check that the sources have at least one parameter for each metric supported by the source."""
        for metric_key, metric in values["metrics"].__root__.items():
            for source_key in metric.sources:
                source = sources.__root__[source_key]
                parameter_metrics = []
                for parameter in source.parameters.__root__.values():
                    parameter_metrics.extend(parameter.metrics)
                if metric_key not in parameter_metrics:
                    raise ValueError(f"No parameters for metric {metric_key} in source {source_key}")

    @classmethod
    def check_metric_supports_source(cls, sources, values):
        """Check that the source parameters refer to metrics that list the source as allowed source."""
        for source_key, source in sources.__root__.items():
            for parameter_key, parameter in source.parameters.__root__.items():
                for metric_key in parameter.metrics:
                    if source_key not in values["metrics"].__root__[metric_key].sources:
                        raise ValueError(
                            f"Parameter {parameter_key} of source {source_key} lists metric {metric_key} as metric "
                            f"needing this parameter, but that metric doesn't list {source_key} as allowed source"
                        )

    @classmethod
    def check_source_configurations(cls, sources, values):
        """Check that the source configurations are for metrics that actually list those sources as possible source."""
        metrics = values["metrics"].__root__
        for source_key, source in sources.__root__.items():
            if source.configuration:
                cls.check_source_configuration(source_key, source.configuration, metrics)

    @classmethod
    def check_source_configuration(cls, source_key, configuration, metrics):
        """Check that the metrics listed by the source configuration have the source as supported source."""
        for configuration_key, configuration_value in configuration.__root__.items():
            for metric_key in configuration_value.metrics:
                if metric_key not in metrics:
                    raise ValueError(
                        f"Configuration {configuration_key} of source {source_key} refers to "
                        f"non-existing metric {metric_key}"
                    )
                if source_key not in metrics[metric_key].sources:
                    raise ValueError(
                        f"Configuration {configuration_key} of source {source_key} refers to metric {metric_key}, "
                        f"but {metric_key} doesn't list {source_key} as source"
                    )

    @classmethod
    def check_quality_time_metric_types(cls, sources, values):
        """Check that Quality-time lists all metric types as possible values for its metric_type parameter."""
        all_metric_names = {metric.name for metric in values["metrics"].__root__.values()}
        all_metric_names.add("Ready user story points")  # Removed in first non-patch version after Quality-time v3.3.0
        quality_time_metric_names = set(sources.__root__.get("quality_time").parameters.__root__["metric_type"].values)
        if all_metric_names != quality_time_metric_names:
            raise ValueError("Parameter metric_type of source quality_time doesn't list all metric types")

    @validator("subjects")
    def check_subjects(cls, subjects, values):  # pylint: disable=no-self-argument,no-self-use
        """Check that each metric belongs to at least one subject."""
        for metric_key in values["metrics"].__root__:
            for subject in subjects.__root__.values():
                if metric_key in subject.metrics:
                    break
            else:
                raise ValueError(f"Metric {metric_key} is not listed in any subject")
        return subjects
