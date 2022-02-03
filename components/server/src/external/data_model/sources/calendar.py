"""Calendar source."""

from ..meta.source import Source
from ..parameters import DateParameter


CALENDAR = Source(
    name="Calendar date",
    description="Return a manually set date. Can be used to, for example, warn when it is time for the next "
    "security test.",
    parameters=dict(
        date=DateParameter(name="Date", mandatory=True, default_value="2022-01-01", metrics=["time_passed"]),
    ),
)
