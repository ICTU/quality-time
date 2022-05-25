"""Source logos."""

import bottle

from shared.data_model.logos import LOGOS_ROOT


@bottle.get("/api/v3/logo/<source_type>", authentication_required=False)
def get_logo(source_type: str):
    """Return the logo for the source type."""
    return bottle.static_file(f"{source_type}.png", root=LOGOS_ROOT, mimetype="image/png")
