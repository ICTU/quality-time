"""Data model configuration."""

from .meta.config import Config

CONFIG = Config(
    # Default desired response times in days, for metric statuses and measurement entity statuses that require action:
    desired_response_times={
        "debt_target_met": 60,
        "near_target_met": 21,
        "target_not_met": 7,
        "unknown": 3,
        "confirmed": 180,
        "false_positive": 180,
        "wont_fix": 180,
        "fixed": 7,
    },
)
