"""Cargo Audit JSON report."""

from shared_data_model.meta.source import Source
from shared_data_model.parameters import access_parameters

CARGO_AUDIT = Source(
    name="Cargo Audit",
    description="Cargo Audit is a linter for Rust Cargo.lock files for crates.",
    url="https://docs.rs/cargo-audit/latest/cargo_audit/",
    parameters=dict(
        **access_parameters(
            ["security_warnings"],
            source_type="Cargo Audit report",
            source_type_format="JSON",
        ),
    ),
    entities={
        "security_warnings": {
            "name": "security warning",
            "attributes": [
                {"name": "Advisory id", "url": "advisory_url"},
                {"name": "Advisory title"},
                {"name": "Package name"},
                {"name": "Package version"},
                {"name": "Versions patched"},
            ],
        },
    },
)
