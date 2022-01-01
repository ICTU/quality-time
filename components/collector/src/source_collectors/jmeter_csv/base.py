"""Base classes for JMeter CSV collectors."""

import csv
from io import StringIO
from typing import AsyncIterator, Literal

from base_collectors import CSVFileSourceCollector
from model import SourceResponses


Samples = list[dict[str, str]]


class JMeterCSVCollector(CSVFileSourceCollector):
    """Base class for JMeter CSV file collectors."""

    @classmethod
    async def _timestamps(cls, responses: SourceResponses) -> set[int]:
        """Return all timestamps in the samples in the responses."""
        timestamps = set()
        async for samples in cls._samples(responses):
            timestamps |= {int(sample["timeStamp"]) for sample in samples}
        return timestamps

    @classmethod
    async def _samples(cls, responses: SourceResponses) -> AsyncIterator[Samples]:
        """Yield the samples grouped by label."""
        rows = await cls.__parse_csv(responses)
        samples = [row for row in rows if not row["responseMessage"].startswith("Number of samples in transaction")]
        labels = {sample["label"] for sample in samples}
        for label in sorted(labels):
            yield [sample for sample in samples if sample["label"] == label]

    @staticmethod
    async def __parse_csv(responses: SourceResponses) -> Samples:
        """Parse the CSV rows from the responses."""
        rows = []
        for response in responses:
            csv_text = await response.text()
            rows.extend(list(csv.DictReader(StringIO(csv_text.strip(), newline=""))))
        return rows

    @classmethod
    def _success_count(cls, samples: Samples) -> int:
        """Return the number of successful samples."""
        return cls.__sample_count(samples, "true")

    @classmethod
    def _error_count(cls, samples: Samples) -> int:
        """Return the number of errored samples."""
        return cls.__sample_count(samples, "false")

    @staticmethod
    def __sample_count(samples: Samples, sample_result: Literal["true", "false"]) -> int:
        """Return the number of samples with the specified sample result."""
        return len([sample for sample in samples if sample["success"] == sample_result])
