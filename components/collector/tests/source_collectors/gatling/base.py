"""Base classes for Gatling collectors."""

from typing import ClassVar

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class GatlingTestCase(SourceCollectorTestCase):
    """Base class for Gatling collector unit tests."""

    SOURCE_TYPE = "gatling"
    API1 = "Foo"
    API2 = "Bar"
    GATLING_JSON: ClassVar[dict[str, dict[str, dict[str, dict[str, str | dict[str, int | float | str]]]]]] = {
        "contents": {
            "transaction1": {
                "stats": {
                    "name": API1,
                    "numberOfRequests": {"total": 123, "ok": 121, "ko": 2},
                    "meanResponseTime": {"total": 110},
                    "minResponseTime": {"total": 50.0},
                    "maxResponseTime": {"total": 250.0000004},
                    "percentiles1": {"total": 100.0},
                    "percentiles2": {"total": 115.0},
                    "percentiles3": {"total": 135.0},
                    "percentiles4": {"total": 195.0},
                },
            },
            "transaction2": {
                "stats": {
                    "name": API2,
                    "numberOfRequests": {"total": 125, "ok": 121, "ko": 4},
                    "meanResponseTime": {"total": 110.56},
                    "minResponseTime": {"total": 40.0},
                    "maxResponseTime": {"total": 2500.03223},
                    "percentiles1": {"total": 90.0},
                    "percentiles2": {"total": 120.0},
                    "percentiles3": {"total": 150.0},
                    "percentiles4": {"total": 190.0},
                },
            },
        },
    }
    GATLING_LOG = """ASSERTION AAECAAIBAAAAAAAAACRA
    RUN     api.CombinedSimulations combinedsimulations     1638907423554           3.3.1
    USER    Get Token       1       START   1638907424543   1638907424543
    REQUEST 1               GetToken        1638907424608   1638907424842   OK
    USER    Get Token       1       END     1638907424543   1638907424919
    USER    FooListSimulation       2       START   1638907434539   1638907434539
    USER    BarListSimulation       3       START   1638907434539   1638907434539
    USER    FooListSimulation       4       START   1638907435040   1638907435040
    USER    BarListSimulation       6       START   1638907435040   1638907435040
    REQUEST 2                FooList 1638907460541   1638907520543   KO      i.g.h.c.i.RequestTimeoutException: \
        Request timeout to app.example.org/1.2.3.4:80 after 60000 ms
    USER    FooListSimulation       2       END     1638907460540   1638907520543
    """
