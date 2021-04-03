"""Unit tests for the Checkmarx CxSAST source version collector."""

from .base import CxSASTTestCase


class CxSASTSourceVersionTest(CxSASTTestCase):
    """Unit tests for the source version collector."""

    METRIC_TYPE = "source_version"
    METRIC_ADDITION = "min"

    async def test_version(self):
        """Test that the version of the source is returned."""
        get_json = [
            [dict(cxVersion="8.6.0.1947")],
        ]
        post_json = dict(access_token="token")
        response = await self.collect(get_request_json_side_effect=get_json, post_request_json_return_value=post_json)
        self.assert_measurement(
            response,
            value="8.6.0.1947",
            landing_url="https://cxsast/CxWebClient",
        )
