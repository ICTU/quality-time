"""JMeter sources."""

from ..meta.entity import EntityAttributeType
from ..meta.source import Source
from ..parameters import access_parameters


ALL_JMETER_METRICS = ["slow_transactions"]

JMETER_JSON = Source(
    name="JMeter JSON",
    description="Apache JMeter application is open source software, a 100% pure Java application designed to load "
    "test functional behavior and measure performance.",
    url="https://jmeter.apache.org",
    parameters=dict(**access_parameters(ALL_JMETER_METRICS, source_type="JMeter report", source_type_format="JSON")),
    entities=dict(
        slow_transactions=dict(
            name="slow transaction",
            attributes=[
                dict(name="Transactions", key="name"),
                dict(name="Sample count"),
                dict(name="Error count", type=EntityAttributeType.INTEGER),
                dict(name="Error percentage", type=EntityAttributeType.FLOAT),
                dict(name="Mean response time (ms)", key="mean_response_time", type=EntityAttributeType.FLOAT),
                dict(name="Median response time (ms)", key="median_response_time", type=EntityAttributeType.FLOAT),
                dict(name="Minimum response time (ms)", key="min_response_time", type=EntityAttributeType.FLOAT),
                dict(name="Maximum response time (ms)", key="max_response_time", type=EntityAttributeType.FLOAT),
                dict(
                    name="90th percentile response time (ms)",
                    key="percentile_90_response_time",
                    type=EntityAttributeType.FLOAT,
                ),
            ],
        )
    ),
)
