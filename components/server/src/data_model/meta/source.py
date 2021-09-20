"""Data model source model."""

import pathlib
from typing import cast, Optional

from pydantic import BaseModel, Field, HttpUrl, validator  # pylint: disable=no-name-in-module

from .base import DescribedModel, NamedModel
from .entity import Entities
from .parameter import Parameters


class Configuration(NamedModel):  # pylint: disable=too-few-public-methods
    """Configuration for specific metrics."""

    metrics: list[str] = Field(..., min_items=1)
    value: list[str] = Field(..., min_items=1)


class Configurations(BaseModel):  # pylint: disable=too-few-public-methods
    """Source configurations."""

    __root__: dict[str, Configuration]


class Source(DescribedModel):  # pylint: disable=too-few-public-methods
    """The source model extends the base model with source parameters and measurement entities."""

    url: Optional[HttpUrl] = None
    configuration: Optional[Configurations] = None
    parameters: Parameters
    entities: Entities = cast(Entities, {})
    issue_tracker: Optional[bool] = False

    @validator("parameters")
    def check_parameters(cls, parameters, values):  # pylint: disable=no-self-argument,no-self-use
        """Check that if the source has a landing URL parameter it also has a URL parameter."""
        source = values["name"]
        if "landing_url" in parameters.__root__ and "url" not in parameters.__root__:
            raise ValueError(f"Source {source} has a landing URL but no URL")
        for parameter_key, parameter in parameters.__root__.items():
            for parameter_to_validate_on in parameter.validate_on or []:
                if parameter_to_validate_on not in parameters.__root__:
                    raise ValueError(
                        f"Source {source} should validate parameter {parameter_key} when parameter "
                        f"{parameter_to_validate_on} changes, but source {source} has no parameter "
                        f"{parameter_to_validate_on}"
                    )
        return parameters


class Sources(BaseModel):
    """Sources mapping."""

    __root__: dict[str, Source]

    @validator("__root__")
    def check_sources(cls, values):  # pylint: disable=no-self-argument,no-self-use
        """Check the sources."""
        cls.check_logos(values)
        cls.check_urls(values)
        cls.check_quality_time_source_types(values)
        return values

    @classmethod
    def check_logos(cls, values):
        """Check that a logo exists for each source and vice versa."""
        logos_path = pathlib.Path(__file__).parent.parent.parent / "routes" / "logos"
        for source_type in values:
            logo_path = logos_path / f"{source_type}.png"
            if not logo_path.exists():
                raise ValueError(f"No logo exists for {source_type}")
        for logo_path in logos_path.glob("*.png"):
            if logo_path.stem not in values:
                raise ValueError(f"No source exists for {logo_path}")

    @classmethod
    def check_urls(cls, values):
        """Check that all sources, except the ones specified below, have a URL."""
        for source_type, source in values.items():
            if source_type not in ("calendar", "manual_number") and not source.url:
                raise ValueError(f"Source {source_type} has no URL")

    @classmethod
    def check_quality_time_source_types(cls, values):
        """Check that Quality-time lists all source types as possible values for its source_type parameter."""
        if quality_time := values.get("quality_time"):  # pragma: no cover-behave
            all_source_names = {source.name for source in values.values()}
            quality_time_source_names = set(quality_time.parameters.__root__["source_type"].values)
            if all_source_names != quality_time_source_names:
                raise ValueError("Parameter source_type of source quality_time doesn't list all source types")
