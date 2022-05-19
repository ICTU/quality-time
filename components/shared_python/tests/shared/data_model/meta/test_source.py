"""Unit tests for the source model."""

from unittest.mock import patch

from shared.data_model.meta.source import Sources

from .base import MetaModelTestCase


@patch("pathlib.Path")
class SourcesTest(MetaModelTestCase):
    """Unit tests for the sources mapping."""

    MODEL = Sources
    DESCRIPTION = "Source."
    URL = "https://example.org"
    SOURCE = dict(name="Source", description=DESCRIPTION, parameters={}, metrics=["metric"])

    @staticmethod
    def mock_path(path_class, exists: bool = True):
        """Return a mock path that does or does not exist."""
        path = path_class.return_value
        path.parent = path
        path.__truediv__.return_value = path
        path.exists.return_value = exists
        return path

    def test_missing_logo(self, path_class):
        """Test that a validation error occurs when a logo is missing."""
        self.mock_path(path_class, exists=False)
        self.check_validation_error("No logo exists for jira", jira=self.SOURCE)

    def test_missing_source(self, path_class):
        """Test that a validation error occurs when a logo exists, but the source is missing."""
        logo_path = self.mock_path(path_class)
        logo_path.glob.return_value = [logo_path]
        logo_path.stem = "non_existing_source"
        self.check_validation_error("No source exists for ", jira=self.SOURCE)

    def test_missing_url(self, path_class):
        """Test that a validation error occurs when a URL is missing."""
        self.mock_path(path_class)
        self.check_validation_error("Source source has no URL", source=self.SOURCE)

    def test_missing_url_parameters(self, path_class):
        """Test that a source with a landing URL parameter also should have a URL parameter."""
        self.mock_path(path_class)
        self.check_validation_error(
            "Source Source has a landing URL but no URL",
            source=dict(
                name="Source",
                description=self.DESCRIPTION,
                url=self.URL,
                parameters=dict(landing_url=dict(name="Landing URL", type="url", metrics=["metric"])),
            ),
        )

    def test_missing_parameter_to_validate_on(self, path_class):
        """Test that a source with a parameter listing another parameter to validate on actually has that parameter."""
        self.mock_path(path_class)
        self.check_validation_error(
            "Source Source should validate parameter url when parameter password changes, "
            "but source Source has no parameter password",
            source=dict(
                name="Source",
                description=self.DESCRIPTION,
                url=self.URL,
                parameters=dict(url=dict(name="URL", type="url", metrics=["metric"], validate_on=["password"])),
            ),
        )

    def test_quality_time_lists_all_source_types(self, path_class):
        """Test that the Quality-time source lists all sources as possible values for its source type parameter."""
        self.mock_path(path_class)
        self.check_validation_error(
            "Parameter source_type of source quality_time doesn't list source types: Quality-time",
            quality_time=dict(
                name="Quality-time",
                description="Quality-time.",
                url="https://quality-time.org",
                parameters=dict(
                    source_type=dict(
                        name="Source type",
                        type="multiple_choice",
                        default_value=[],
                        metrics=["metric"],
                        placeholder="all",
                        values=["foo", "bar"],
                    )
                ),
            ),
        )
