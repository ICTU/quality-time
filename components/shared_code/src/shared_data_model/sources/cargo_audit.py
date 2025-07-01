"""Cargo Audit JSON report."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Entity, EntityAttribute
from shared_data_model.meta.source import Source
from shared_data_model.parameters import FixAvailability, MultipleChoiceWithDefaultsParameter, access_parameters

CARGO_AUDIT = Source(
    name="Cargo Audit",
    description="Cargo Audit is a linter for Rust Cargo.lock files for crates.",
    url=HttpUrl("https://docs.rs/cargo-audit/latest/cargo_audit/"),
    parameters={
        "warning_types": MultipleChoiceWithDefaultsParameter(
            name="Warning types",
            help="If provided, only count security warnings with the selected warning types.",
            placeholder="all warning types",
            values=["vulnerability", "unsound", "yanked"],
            metrics=["security_warnings"],
        ),
        "fix_availability": FixAvailability(),
        **access_parameters(["security_warnings"], source_type="Cargo Audit report", source_type_format="JSON"),
    },
    entities={
        "security_warnings": Entity(
            name="security warning",
            attributes=[
                EntityAttribute(name="Advisory id", url="advisory_url"),
                EntityAttribute(name="Advisory title"),
                EntityAttribute(name="Warning type"),
                EntityAttribute(name="Package name"),
                EntityAttribute(name="Package version"),
                EntityAttribute(name="Versions patched"),
            ],
        ),
    },
)
