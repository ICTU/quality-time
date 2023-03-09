"""Calendar source."""

from datetime import date

from ..meta.source import Source
from ..parameters import DateParameter


CALENDAR = Source(
    name="Calendar date",
    description="Specify a specific date in the past or the future. Can be used to, for example, warn when it is time "
    "for the next security test.",
    parameters=dict(
        date=DateParameter(
            name="Date", mandatory=True, default_value=date.today().strftime("%Y-%m-%d"),
            metrics=["source_up_to_dateness", "time_remaining"]
        ),
    ),
)
