"""Cargo Audit JSON report."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Entity, EntityAttribute
from shared_data_model.meta.source import Source
from shared_data_model.parameters import access_parameters

CARGO_AUDIT = Source(
    name="Cargo Audit",
    description="Cargo Audit is a linter for Rust Cargo.lock files for crates.",
    url=HttpUrl("https://docs.rs/cargo-audit/latest/cargo_audit/"),
    parameters=access_parameters(["security_warnings"], source_type="Cargo Audit report", source_type_format="JSON"),
    entities={
        "security_warnings": Entity(
            name="security warning",
            attributes=[
                EntityAttribute(name="Advisory id", url="advisory_url"),
                EntityAttribute(name="Advisory title"),
                EntityAttribute(name="Package name"),
                EntityAttribute(name="Package version"),
                EntityAttribute(name="Versions patched"),
            ],
        ),
    },
)
