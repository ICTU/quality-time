"""Unit tests for the source model."""

from shared_data_model.meta.source import Source

from .base import MetaModelTestCase


class SourceTest(MetaModelTestCase):
    """Unit tests for the source model."""

    MODEL = Source
    DESCRIPTION = "Source."
    URL = "https://example.org"

    def test_missing_parameter_to_validate_on(self):
        """Test that a source with a parameter listing another parameter to validate on actually has that parameter."""
        model_kwargs = {
            "name": "Source",
            "description": self.DESCRIPTION,
            "url": self.URL,
            "parameters": {
                "url": {"name": "URL", "type": "url", "metrics": ["metric"], "validate_on": ["password"]},
            },
        }
        self.check_validation_error(
            "Source Source should validate parameter url when parameter password changes, "
            "but source Source has no parameter password",
            **model_kwargs,
        )

    def test_missing_url_when_landing_url(self):
        """Test that a source that has a landing url also has a url parameter."""
        model_kwargs = {
            "name": "Source",
            "description": self.DESCRIPTION,
            "parameters": {
                "landing_url": {"name": "URL", "type": "url", "metrics": ["metric"]},
            },
        }
        self.check_validation_error("Source Source has a landing URL but no URL", **model_kwargs)
