"""Data model model."""

import pathlib
from typing import Self

from pydantic import BaseModel, model_validator

from .metric import Metric
from .scale import Scale
from .source import Source
from .subject import Subject


class DataModel(BaseModel):
    """Data model model."""

    scales: dict[str, Scale]
    metrics: dict[str, Metric]
    sources: dict[str, Source]
    subjects: dict[str, Subject]

    @model_validator(mode="after")
    def check_scales(self) -> Self:
        """Check that the metric scales are valid scales."""
        scales = set(self.scales.keys())
        used_scales = set()
        for metric in self.metrics.values():
            metric_scales = set(metric.scales)
            if not metric_scales <= scales:
                msg = f"Metric '{metric.name}' has invalid scales {metric_scales - scales}"
                raise ValueError(msg)
            used_scales |= metric_scales
        if scales - used_scales:
            msg = f"Unused scales {scales - used_scales}"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def check_sources(self) -> Self:
        """Check that the sources are valid."""
        self.check_source_urls()
        self.check_logos()
        self.check_source_has_parameters_for_each_supported_metric()
        self.check_metric_supports_source()
        self.check_source_configurations()
        self.check_quality_time_metric_types()
        self.check_quality_time_source_types()
        return self

    def check_source_urls(self) -> None:
        """Check that all sources, except the ones specified below, have a URL."""
        for source_type, source in self.sources.items():
            if source_type not in ("calendar", "generic_json", "manual_number") and not source.url:
                msg = f"Source {source_type} has no URL"
                raise ValueError(msg)

    def check_logos(self) -> None:
        """Check that a logo exists for each source and vice versa."""
        logos_path = pathlib.Path(__file__).parent.parent / "logos"
        for source_type in self.sources:
            logo_path = logos_path / f"{source_type}.png"
            if not logo_path.exists():
                msg = f"No logo exists for {source_type}"
                raise ValueError(msg)
        for logo_path in logos_path.glob("*.png"):
            if logo_path.stem not in self.sources:
                msg = f"No source exists for {logo_path}"
                raise ValueError(msg)

    def check_source_has_parameters_for_each_supported_metric(self) -> None:
        """Check that the sources have at least one parameter for each metric supported by the source."""
        for metric_key, metric in self.metrics.items():
            for source_key in metric.sources:
                source = self.sources[source_key]
                parameter_metrics = []
                for parameter in source.parameters.values():
                    parameter_metrics.extend(parameter.metrics)
                if metric_key not in parameter_metrics:
                    msg = f"No parameters for metric {metric_key} in source {source_key}"
                    raise ValueError(msg)

    def check_metric_supports_source(self) -> None:
        """Check that the source parameters refer to metrics that list the source as allowed source."""
        for source_key, source in self.sources.items():
            for parameter_key, parameter in source.parameters.items():
                for metric_key in parameter.metrics:
                    if source_key not in self.metrics[metric_key].sources:
                        msg = (
                            f"Parameter {parameter_key} of source {source_key} lists metric {metric_key} as metric "
                            f"needing this parameter, but that metric doesn't list {source_key} as allowed source"
                        )
                        raise ValueError(msg)

    def check_source_configurations(self) -> None:
        """Check that the source configurations are for metrics that actually list those sources as possible source."""
        for source_key, source in self.sources.items():
            if source.configuration:
                self.check_source_configuration(source_key, source.configuration)

    def check_source_configuration(self, source_key, configuration) -> None:
        """Check that the metrics listed by the source configuration have the source as supported source."""
        for configuration_key, configuration_value in configuration.items():
            for metric_key in configuration_value.metrics:
                if metric_key not in self.metrics:
                    msg = (
                        f"Configuration {configuration_key} of source {source_key} refers to non-existing metric "
                        f"{metric_key}"
                    )
                    raise ValueError(msg)
                if source_key not in self.metrics[metric_key].sources:
                    msg = (
                        f"Configuration {configuration_key} of source {source_key} refers to metric {metric_key}, "
                        f"but {metric_key} doesn't list {source_key} as source"
                    )
                    raise ValueError(msg)

    def check_quality_time_metric_types(self) -> None:
        """Check that Quality-time lists all metric types as possible values for its metric_type parameter."""
        all_metric_names = {metric.name for metric in self.metrics.values()}
        quality_time_metric_names = set(self.sources["quality_time"].parameters["metric_type"].values or [])
        if all_metric_names != quality_time_metric_names:
            msg = "Parameter metric_type of source quality_time doesn't list all metric types"
            raise ValueError(msg)

    def check_quality_time_source_types(self) -> None:
        """Check that Quality-time lists all source types as possible values for its source_type parameter."""
        all_source_names = {source.name for source in self.sources.values()}
        quality_time_source_names = set(self.sources["quality_time"].parameters["source_type"].values or [])
        if all_source_names != quality_time_source_names:
            msg = (
                f"Parameter source_type of source quality_time doesn't list source types: "
                f"{', '.join(all_source_names - quality_time_source_names)}"
            )
            raise ValueError(msg)

    @model_validator(mode="after")
    def check_subjects(self) -> Self:
        """Check that each metric belongs to at least one subject."""
        for metric_key in self.metrics:
            for subject in self.subjects.values():
                if metric_key in subject.metrics:
                    break
            else:
                msg = f"Metric {metric_key} is not listed in any subject"
                raise ValueError(msg)
        return self
