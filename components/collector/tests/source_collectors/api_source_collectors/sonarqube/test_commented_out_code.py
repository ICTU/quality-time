"""Unit tests for the SonarQube commented-out code collector."""

from .base import SonarQubeTestCase


class SonarQubeCommentedOutCodeTest(SonarQubeTestCase):
    """Unit tests for the SonarQube commented-out code collector."""

    async def test_commented_out_code(self):
        """Test that the number of lines with commented out code is returned."""
        json = dict(total="2")
        metric = dict(type="commented_out_code", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=json)
        self.assert_measurement(
            response,
            value="2",
            total="100",
            landing_url=f"{self.issues_landing_url}&rules=abap:S125,apex:S125,c:CommentedCode,cpp:CommentedCode,"
            "flex:CommentedCode,csharpsquid:S125,javascript:CommentedCode,javascript:S125,kotlin:S125,"
            "objc:CommentedCode,php:S125,plsql:S125,python:S125,scala:S125,squid:CommentedOutCodeLine,"
            "java:S125,swift:S125,typescript:S125,Web:AvoidCommentedOutCodeCheck,xml:S125",
        )
