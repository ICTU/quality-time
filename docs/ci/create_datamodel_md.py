"""Script to convert the data model in a Markdown file."""

import json
import os
import pathlib
from typing import List


def data_model():
    """Return the data model."""
    data_model_path = pathlib.Path(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "components", "server", "src", "data", "datamodel.json")
    with open(data_model_path) as json_data_model:
        return json.load(json_data_model)


def markdown_table_row(*cells: str) -> str:
    """Return a Markdown table row."""
    return f"| {' | '.join(cells)} |\n"


def markdown_table_header(*column_headers: str) -> str:
    """Return a Markdown table header."""
    headers = markdown_table_row(*column_headers)
    separator = markdown_table_row(*["-" * len(column_header) for column_header in column_headers])
    return headers + separator


def markdown_header(header: str, level: int = 1) -> str:
    """Return a Markdown header."""
    return "#" * level + f" {header}\n\n"


def metrics_table(dm, universal_sources: List[str]) -> str:
    """Return the metrics as Markdown table."""
    markdown = markdown_table_header("Name", "Description", "Default target", "Default tags", "Sources¹")
    for metric_key, metric in dm["metrics"].items():
        direction = {"<": "≦", ">": "≧"}[metric['direction']]
        unit = f"% of the " + metric["unit"] if metric["default_scale"] == "percentage" else " " + metric["unit"]
        target = f"{direction} {metric['target']}{unit}"
        tags = ", ".join(metric['tags'])
        sources = ", ".join(
            [dm["sources"][source]['name'] for source in metric["sources"] if source not in universal_sources])
        markdown += markdown_table_row(metric['name'], metric['description'], target, tags, sources)
    markdown += "\n"
    return markdown


def sources_table(dm, universal_sources: List[str]) -> str:
    """Return the sources as Markdown table."""
    markdown = markdown_table_header("Name", "Description", "Metrics")
    for source_key, source in dm["sources"].items():
        name = f"[{source['name']}]({source['url']})" if "url" in source else source['name']
        if source_key in universal_sources:
            metrics = "¹"
        else:
            metrics = ", ".join(
                [metric["name"] for metric in dm["metrics"].values() if source_key in metric["sources"]])
        markdown += markdown_table_row(name, source['description'], metrics)
    markdown += "\n"
    return markdown


def data_model_as_table(dm) -> str:
    """Return the data model as Markdown table."""
    markdown = markdown_header("Quality-time data model")
    markdown += markdown_header("Quality-time metrics", 2)
    markdown += metrics_table(dm, universal_sources := ["manual_number", "random"])
    markdown += markdown_header("Quality-time sources", 2)
    markdown += sources_table(dm, universal_sources)
    markdown += "¹) All metrics can be measured using the 'Manual number' and the 'Random number' source.\n"
    return markdown


if __name__ == "__main__":
    data_model_md_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)), "..", "DATA_MODEL.md")
    with open(data_model_md_path, "w") as data_model_md:
        data_model_md.write(data_model_as_table(data_model()))
