"""Calendar source."""

from ..meta.source import Source
from ..parameters import DateParameter


CALENDAR = Source(
    name="Calendar date",
    description="Warn when the date is too long ago. Can be used to, for example, warn when it is time for the next "
    "security test.",
    parameters=dict(
        date=DateParameter(name="Date", mandatory=True, default_value="2021-01-01", metrics=["source_up_to_dateness"]),
    ),
)
