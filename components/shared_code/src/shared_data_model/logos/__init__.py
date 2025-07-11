"""Logos for sources."""

import importlib.resources


def get_logo(name: str) -> bytes:
    """Return the logo."""
    return importlib.resources.read_binary("shared_data_model.logos", f"{name}.png")


def get_logo_names() -> list[str]:
    """Return the logo names."""
    with importlib.resources.path("shared_data_model", "logos") as logos:
        return [logo.name.removesuffix(".png") for logo in logos.glob("*.png")]
