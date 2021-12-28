"""Base classes for Gatling JSON collectors."""

from ..source_collector_test_case import SourceCollectorTestCase


class GatlingJSONTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for Gatling JSON collector unit tests."""

    SOURCE_TYPE = "gatling_json"
    API1 = "Foo"
    API2 = "Bar"
    GATLING_JSON = dict(
        contents=dict(
            transaction1=dict(
                stats=dict(
                    name=API1,
                    numberOfRequests=dict(total=123, ok=121, ko=2),
                    meanResponseTime=dict(total=110),
                    minResponseTime=dict(total=50.0),
                    maxResponseTime=dict(total=250.0000004),
                    percentiles1=dict(total=100.0),
                    percentiles2=dict(total=115.0),
                    percentiles3=dict(total=135.0),
                    percentiles4=dict(total=195.0),
                )
            ),
            transaction2=dict(
                stats=dict(
                    name=API2,
                    numberOfRequests=dict(total=125, ok=121, ko=4),
                    meanResponseTime=dict(total=110.56),
                    minResponseTime=dict(total=40.0),
                    maxResponseTime=dict(total=2500.03223),
                    percentiles1=dict(total=90.0),
                    percentiles2=dict(total=120.0),
                    percentiles3=dict(total=150.0),
                    percentiles4=dict(total=190.0),
                )
            ),
        )
    )
