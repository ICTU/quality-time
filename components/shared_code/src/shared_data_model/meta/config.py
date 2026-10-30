"""Data model configuration."""

from pydantic import BaseModel, PositiveInt


class Config(BaseModel):
    """Base model for configuration settings."""

    desired_response_times: dict[str, PositiveInt]  # Default desired response times in days
