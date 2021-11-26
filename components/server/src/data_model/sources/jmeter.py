"""JMeter sources."""

from ..meta.source import Source
from ..parameters import access_parameters


ALL_JMETER_METRICS = ["slow_transactions"]

JMETER_JSON = Source(
    name="JMeter JSON",
    description="Apache JMeter application is open source software, a 100% pure Java application designed to load "
    "test functional behavior and measure performance.",
    url="https://jmeter.apache.org",
    parameters=dict(**access_parameters(ALL_JMETER_METRICS, source_type="JMeter report", source_type_format="JSON")),
)
