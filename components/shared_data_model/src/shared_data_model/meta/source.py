"""Data model source model."""

from __future__ import annotations

import pathlib
from typing import cast

from pydantic import Field, HttpUrl, validator

from .base import DescribedModel, MappedModel, NamedModel
from .entity import Entities
from .parameter import Parameter, Parameters


class Configuration(NamedModel):
    """Configuration for specific metrics."""

    metrics: list[str] = Field(..., min_items=1)
    value: list[str] = Field(..., min_items=1)


class Configurations(MappedModel[Configuration]):
    """Source configurations."""


class Documentation(MappedModel[str]):
    """Source documentation for specific metrics."""


class Source(DescribedModel):
    """The source model extends the base model with source parameters and measurement entities."""

    url: HttpUrl | None = None
    documentation: Documentation | None = None  # Documentation in Markdown format
    configuration: Configurations = cast(Configurations, {})
    parameters: Parameters
    entities: Entities = cast(Entities, {})
    issue_tracker: bool | None = False

    @validator("parameters")
    def check_parameters(cls, parameters: Parameters, values) -> Parameters:
        """Check that if the source has a landing URL parameter it also has a URL parameter."""
        source = values["name"]
        if "landing_url" in parameters.__root__ and "url" not in parameters.__root__:
            msg = f"Source {source} has a landing URL but no URL"
            raise ValueError(msg)
        for parameter_key, parameter in cast(dict[str, Parameter], parameters.__root__).items():
            for parameter_to_validate_on in parameter.validate_on or []:
                if parameter_to_validate_on not in parameters.__root__:
                    msg = (
                        f"Source {source} should validate parameter {parameter_key} when parameter "
                        f"{parameter_to_validate_on} changes, but source {source} has no parameter "
                        f"{parameter_to_validate_on}"
                    )
                    raise ValueError(msg)
        return parameters


class Sources(MappedModel[Source]):
    """Sources mapping."""

    @validator("__root__")
    def check_sources(cls, values: dict) -> dict:
        """Check the sources."""
        cls.check_logos(values)
        cls.check_urls(values)
        cls.check_quality_time_source_types(values)
        return values

    @classmethod
    def check_logos(cls, values: dict) -> None:
        """Check that a logo exists for each source and vice versa."""
        logos_path = pathlib.Path(__file__).parent.parent / "logos"
        for source_type in values:
            logo_path = logos_path / f"{source_type}.png"
            if not logo_path.exists():
                msg = f"No logo exists for {source_type}"
                raise ValueError(msg)
        for logo_path in logos_path.glob("*.png"):
            if logo_path.stem not in values:
                msg = f"No source exists for {logo_path}"
                raise ValueError(msg)

    @classmethod
    def check_urls(cls, values: dict) -> None:
        """Check that all sources, except the ones specified below, have a URL."""
        for source_type, source in values.items():
            if source_type not in ("calendar", "generic_json", "manual_number") and not source.url:
                msg = f"Source {source_type} has no URL"
                raise ValueError(msg)

    @classmethod
    def check_quality_time_source_types(cls, values: dict) -> None:
        """Check that Quality-time lists all source types as possible values for its source_type parameter."""
        if quality_time := values.get("quality_time"):  # pragma: no feature-test-cover
            all_source_names = {source.name for source in values.values()}
            quality_time_source_names = set(quality_time.parameters.__root__["source_type"].values)
            if all_source_names != quality_time_source_names:
                msg = (
                    f"Parameter source_type of source quality_time doesn't list source types: "
                    f"{', '.join(all_source_names - quality_time_source_names)}"
                )
                raise ValueError(msg)
