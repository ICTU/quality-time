"""Calendar source."""

from datetime import date

from shared_data_model.meta.parameter import ParameterGroup
from shared_data_model.meta.source import Source
from shared_data_model.parameters import DateParameter, IntegerParameter, SingleChoiceParameter

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
        # Note that the recurrence parameters are only used by the frontend (for allowing the user to set a next date),
        # and not by the collector:
        "recurrence_frequency": IntegerParameter(
            name="Recurrence frequency",
            help="The number of days/weeks/months/years with which to increase the date when setting the next date.",
            default_value="0",
            unit="",
            metrics=["time_remaining"],
        ),
        "recurrence_unit": SingleChoiceParameter(
            name="Recurrence unit",
            help="The unit with which to increase the date when setting the next date.",
            default_value="day",
            values=["day", "week", "month", "year"],
            metrics=["time_remaining"],
        ),
        "recurrence_offset": SingleChoiceParameter(
            name="Recurrence offset",
            help="Date from which to set the next date.",
            default_value="today",
            values=["today", "previous date"],
            metrics=["time_remaining"],
        ),
    },
    parameter_layout={
        "date": ParameterGroup(name="Manual source data"),
    },
)
