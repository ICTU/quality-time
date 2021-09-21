"""Internal server."""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from routes import data_model, health, measurements, metrics


app = FastAPI()
for module in data_model, health, measurements, metrics:
    # DeepSource complains that getattr doesn't receive a default value and will cause an AttributeError if the
    # attribute does not exist. As we do want to fail if the module has no router, we suppress the rule here.
    app.include_router(getattr(module, "router"))  # skipcq: PTC-W0034


@app.get("/")
def redirect_to_docs():
    """Redirect / to /docs."""
    return RedirectResponse(url="/docs")
