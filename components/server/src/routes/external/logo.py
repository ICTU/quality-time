"""Source logo's."""

import pathlib

import bottle


LOGOS_ROOT = pathlib.Path(__file__).parent.absolute().joinpath(pathlib.Path("logos"))


@bottle.get("/api/v3/logo/<source_type>", authentication_required=False)
def get_logo(source_type: str):
    """Return the logo for the source type."""
    return bottle.static_file(f"{source_type}.png", root=LOGOS_ROOT, mimetype="image/png")
