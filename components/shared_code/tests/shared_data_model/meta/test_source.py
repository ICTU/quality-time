"""Unit tests for the source model."""

from shared_data_model.meta.source import Source

from .base import MetaModelTestCase


class SourceTest(MetaModelTestCase):
    """Unit tests for the source model."""

    def check_source_validation_error(self, expected_message: str, **extra_model_kwargs) -> None:
        """Extend to add the model."""
        model_kwargs = {"name": "Source", "description": "Source."}
        self.check_validation_error(expected_message, Source, **(model_kwargs | extra_model_kwargs))

    def test_missing_parameter_to_validate_on(self):
        """Test that a source with a parameter listing another parameter to validate on actually has that parameter."""
        extra_model_kwargs = {
            "url": "https://example.org",
            "parameters": {
                "url": {"name": "URL", "type": "url", "metrics": ["metric"], "validate_on": ["password"]},
            },
        }
        self.check_source_validation_error(
            "Source Source should validate parameter url when parameter password changes, "
            "but source Source has no parameter password",
            **extra_model_kwargs,
        )

    def test_missing_url_when_landing_url(self):
        """Test that a source that has a landing URL also has a URL parameter."""
        extra_model_kwargs = {
            "parameters": {
                "landing_url": {"name": "URL", "type": "url", "metrics": ["metric"]},
            },
        }
        self.check_source_validation_error("Source Source has a landing URL but no URL", **extra_model_kwargs)

    def test_missing_url_when_deprecated(self):
        """Test that a source that is deprecated also has a deprecation URL parameter."""
        extra_model_kwargs = {"deprecated": True, "parameters": {}}
        self.check_source_validation_error(
            "Source Source is deprecated but has no deprecation URL",
            **extra_model_kwargs,
        )

    def test_missing_github_pat_parameter(self):
        """Test that a source with a repository URL also has a GitHub PAT."""
        extra_model_kwargs = {
            "repository_url": "https://github.com/ICTU/quality-time",
            "parameters": {"url": {"name": "UR:", "type": "url", "metrics": ["metric"]}},
        }
        self.check_source_validation_error(
            "Source Source has a repository URL but no GitHub personal access token parameter.",
            **extra_model_kwargs,
        )

    def test_missing_repository_url(self):
        """Test that a source with a GitHub PAT also has a repository URL."""
        extra_model_kwargs = {
            "parameters": {
                "url": {"name": "UR:", "type": "url", "metrics": ["metric"]},
                "github_pat": {"name": "GitHub PAT", "type": "password", "metrics": ["metric"]},
            },
        }
        self.check_source_validation_error(
            "Source Source has a GitHub personal access token parameter but no repository URL.",
            **extra_model_kwargs,
        )
