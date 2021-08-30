"""Health endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def get_health() -> dict[str, bool]:
    """Return the internal-server health status."""
    return {"healthy": True}
