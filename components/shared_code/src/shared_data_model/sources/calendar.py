"""Calendar source."""

from datetime import date

from shared_data_model.meta.source import Source
from shared_data_model.parameters import DateParameter

CALENDAR = Source(
    name="Calendar date",
    description="Specify a specific date in the past or the future. Can be used to, for example, warn when it is time "
    "for the next security test.",
    parameters={
        "date": DateParameter(
            name="Date",
            mandatory=True,
            default_value=date.today().strftime("%Y-%m-%d"),  # noqa: DTZ011
            metrics=["source_up_to_dateness", "time_remaining"],
        ),
    },
)
