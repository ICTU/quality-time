"""Base classes for JMeter JSON collectors."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class JMeterJSONTestCase(SourceCollectorTestCase):
    """Base class for JMeter JSON collector unit tests."""

    SOURCE_TYPE = "jmeter_json"
    API1 = "/api/foo"
    API2 = "/api/bar"
    JMETER_JSON = {
        "transaction1": {
            "transaction": API1,
            "sampleCount": 123,
            "errorCount": 2,
            "errorPct": 2 / 123,
            "meanResTime": 110,
            "medianResTime": 120,
            "minResTime": 50.0,
            "maxResTime": 250.0000004,
            "pct1ResTime": 115.0,
            "pct2ResTime": 135.0,
            "pct3ResTime": 195.0,
        },
        "transaction2": {
            "transaction": API2,
            "sampleCount": 125,
            "errorCount": 4,
            "errorPct": 4 / 125,
            "meanResTime": 110.56,
            "medianResTime": 130,
            "minResTime": 40.0,
            "maxResTime": 2500.03223,
            "pct1ResTime": 120.0,
            "pct2ResTime": 150.0,
            "pct3ResTime": 190.0,
        },
        "Total": {},  # Total should be ignored
    }
