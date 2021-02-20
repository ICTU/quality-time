"""Unit tests for the Checkmarx CxSAST security warnings collector."""

from .base import CxSASTTestCase


class CxSASTSecurityWarningsTest(CxSASTTestCase):
    """Unit tests for the security warnings collector."""

    METRIC_TYPE = "security_warnings"

    async def test_nr_of_warnings(self):
        """Test that the number of security warnings is returned."""
        get_json = [
            [dict(name="project", id="id")],
            [dict(id=1000)],
            dict(highSeverity=1, mediumSeverity=2, lowSeverity=3, infoSeverity=4),
            [dict(name="project", id="id")],
            [dict(id="scan_id")],
        ]
        post_json = dict(access_token="token")
        response = await self.collect(get_request_json_side_effect=get_json, post_request_json_return_value=post_json)
        self.assert_measurement(response, value="10", entities=[])
