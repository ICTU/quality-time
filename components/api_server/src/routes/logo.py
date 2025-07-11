"""Source logos."""

from bottle import abort, get, response

from shared_data_model import DATA_MODEL
from shared_data_model.logos import get_logo as get_logo_png


@get("/api/internal/logo/<source_type>", authentication_required=False)
def get_logo(source_type: str):
    """Return the logo for the source type."""
    if source_type not in DATA_MODEL.sources:  # pragma: no feature-test-cover
        return abort(404, f"Logo not found: '{source_type}' is not a valid source type")
    response.set_header("Content-Type", "image/png")
    return get_logo_png(source_type)
