"""Unit tests for the Checkmarx CxSAST source up-to-dateness collector."""

from datetime import datetime, timezone

from .base import CxSASTTestCase


class CxSASTSourceUpToDatenessTest(CxSASTTestCase):
    """Unit tests for the source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_age(self):
        """Test that the age of the last finished scan is returned."""
        get_json = [
            [dict(name="project", id="id")],
            [dict(id="scan_id")],
            [dict(dateAndTime=dict(finishedOn="2019-01-01T09:06:12+00:00"))],
        ]
        post_json = dict(access_token="token")
        response = await self.collect(get_request_json_side_effect=get_json, post_request_json_return_value=post_json)
        expected_age = (datetime.now(timezone.utc) - datetime(2019, 1, 1, 9, 6, 9, tzinfo=timezone.utc)).days
        self.assert_measurement(
            response,
            value=str(expected_age),
            landing_url="https://cxsast/CxWebClient/ViewerMain.aspx?scanId=scan_id&ProjectID=id",
        )

    async def test_landing_url_without_response(self):
        """Test that a default landing url is returned when connecting to the source fails."""
        response = await self.collect(post_request_side_effect=RuntimeError)
        self.assert_measurement(response, landing_url="https://cxsast/CxWebClient", connection_error="Traceback")
