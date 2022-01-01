"""Base classes for Gatling log collectors."""

from ..source_collector_test_case import SourceCollectorTestCase


class GatlingLogTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for Gatling log collector unit tests."""

    SOURCE_TYPE = "gatling_log"

    GATLING_LOG = """RUN     api.CombinedSimulations combinedsimulations     1638907423554           3.3.1
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
