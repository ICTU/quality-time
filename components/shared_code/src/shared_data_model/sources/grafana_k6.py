"""Grafana k6 sources."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import access_parameters

FLOAT = EntityAttributeType.FLOAT
HELP = "response time (milliseconds)"

GRAFANA_K6 = Source(
    name="Grafana k6",
    description=(
        "K6 is an open-source load testing tool developed by Grafana Labs. It is designed to help developers test "
        "the performance and reliability of their systems."
    ),
    url=HttpUrl("https://k6.io"),
    parameters={
        **access_parameters(["slow_transactions"], source_type="Grafana k6 summary.json", source_type_format="JSON"),
    },
    entities={
        "slow_transactions": Entity(
            name="slow transaction",
            attributes=[
                EntityAttribute(name="Transaction", key="name"),
                EntityAttribute(name="Thresholds"),
                EntityAttribute(name="Sample count", key="count", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Average", help=f"Average {HELP}", key="average_response_time", type=FLOAT),
                EntityAttribute(name="Median", help=f"Median {HELP}", key="median_response_time", type=FLOAT),
                EntityAttribute(name="Minimum", help=f"Minimim {HELP}", key="min_response_time", type=FLOAT),
                EntityAttribute(name="Maximum", help=f"Maximum {HELP}", key="max_response_time", type=FLOAT),
            ],
        )
    },
)
