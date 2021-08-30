"""Internal server."""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from routes import data_model, health, measurements, metrics


app = FastAPI()
for module in data_model, health, measurements, metrics:
    app.include_router(getattr(module, "router"))


@app.get("/")
def redirect_to_docs():
    """Redirect / to /docs."""
    return RedirectResponse(url="/docs")
