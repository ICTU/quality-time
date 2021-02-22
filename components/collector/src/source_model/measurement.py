"""Source measurement model class."""

from collector_utilities.type import ErrorMessage, Value
from source_model import Entity


class SourceMeasurement:  # pylint: disable=too-few-public-methods
    """Class to hold measurement values, entities, and error messages from collecting the measurement from one
    source."""

    MAX_ENTITIES = 100  # The maximum number of entities (e.g. violations, warnings) to send to the server

    def __init__(
        self,
        *,
        value: Value = None,
        total: Value = "100",
        entities: list[Entity] = None,
        parse_error: ErrorMessage = None
    ) -> None:
        self.value = str(len(entities)) if value is None and entities is not None else value
        self.total = total
        self.entities = entities[: self.MAX_ENTITIES] if entities else []
        self.parse_error = parse_error
