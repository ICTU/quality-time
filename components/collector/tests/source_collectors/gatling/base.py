"""Base classes for Gatling collectors."""

from ..source_collector_test_case import SourceCollectorTestCase


class GatlingTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for Gatling collector unit tests."""

    SOURCE_TYPE = "gatling"
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
    GATLING_LOG = """ASSERTION AAECAAIBAAAAAAAAACRA
    RUN     api.CombinedSimulations combinedsimulations     1638907423554           3.3.1
    USER    Get Token       1       START   1638907424543   1638907424543
    REQUEST 1               GetToken        1638907424608   1638907424842   OK
    USER    Get Token       1       END     1638907424543   1638907424919
    USER    FooListSimulation       2       START   1638907434539   1638907434539
    USER    BarListSimulation       3       START   1638907434539   1638907434539
    USER    FooListSimulation       4       START   1638907435040   1638907435040
    USER    BarListSimulation       6       START   1638907435040   1638907435040
    REQUEST 2                FooList 1638907460541   1638907520543   KO      i.g.h.c.i.RequestTimeoutException: Request timeout to app.example.org/1.2.3.4:80 after 60000 ms
    USER    FooListSimulation       2       END     1638907460540   1638907520543
    """
