"""Unit tests for the cloc source."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class ClocTest(SourceCollectorTestCase):
    """Unit tests for the cloc metrics."""

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type="cloc", parameters=dict(url="https://cloc.json")))

    async def test_loc(self):
        """Test that the number of lines is returned and that the languages are returned as entities."""
        cloc_json = {
            "header": {}, "SUM": {},  # header and SUM are not used
            "Python": {"nFiles": 1, "blank": 5, "comment": 10, "code": 60},
            "JavaScript": {"nFiles": 1, "blank": 2, "comment": 0, "code": 30}}
        expected_entities = [
            dict(key="Python", language="Python", nr_files="1", blank="5", comment="10", code="60"),
            dict(key="JavaScript", language="JavaScript", nr_files="1", blank="2", comment="0", code="30")]
        metric = dict(type="loc", sources=self.sources, addition="sum")
        response = await self.collect(metric, get_request_json_return_value=cloc_json)
        self.assert_measurement(response, value="90", total="90", entities=expected_entities)
