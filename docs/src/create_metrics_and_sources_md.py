"""Script to convert the data model in a Markdown file."""

import json
import pathlib
import re
import sys

TYPE_DESCRIPTION = dict(
    url="URL",
    string="String",
    multiple_choice="Multiple choice",
    password="Password",
    integer="Integer",
    date="Date",
    single_choice="Single choice",
    multiple_choice_with_addition="Multiple choice with addition",
)


def html_escape(text: str) -> str:
    """Escape < and >."""
    return text.replace("<", "&lt;").replace(">", "&gt;")


def get_data_model():
    """Return the data model."""
    module_dir = pathlib.Path(__file__).resolve().parent
    server_src_path = module_dir.parent.parent / "components" / "server" / "src"
    sys.path.insert(0, str(server_src_path))
    from data.data_model import DATA_MODEL_JSON  # pylint: disable=import-error,import-outside-toplevel

    return json.loads(DATA_MODEL_JSON)


def markdown_link(url: str, anchor: str = None) -> str:
    """Return a Markdown link."""
    anchor = anchor or url
    return f"[{anchor}]({url})"


def markdown_table_row(*cells: str) -> str:
    """Return a Markdown table row."""
    return f"| {' | '.join([html_escape(cell) for cell in cells])} |\n"


def markdown_table_header(*column_headers: str) -> str:
    """Return a Markdown table header."""
    headers = markdown_table_row(*column_headers)
    separator = markdown_table_row(*[":" + "-" * (len(column_header) - 1) for column_header in column_headers])
    return "\n" + headers + separator


def markdown_header(header: str, level: int = 1) -> str:
    """Return a Markdown header."""
    return ("\n" if level > 1 else "") + "#" * level + f" {header}\n"


def metrics_table(data_model, universal_sources: list[str]) -> str:
    """Return the metrics as Markdown table."""
    markdown = markdown_table_header("Name", "Description", "Default target", "Scale(s)", "Default tags", "Sources¹")
    for metric in sorted(data_model["metrics"].values(), key=lambda item: str(item["name"])):
        direction = {"<": "≦", ">": "≧"}[metric["direction"]]
        unit = "% of the " + metric["unit"] if metric["default_scale"] == "percentage" else " " + metric["unit"]
        target = f"{direction} {metric['target']}{unit}"
        if len(metric["scales"]) == 1:
            scales = metric["default_scale"]
        else:
            scales = ", ".join(
                [
                    f"{scale} (default)" if scale == metric["default_scale"] else scale
                    for scale in sorted(metric["scales"])
                ]
            )
        tags = ", ".join(metric["tags"])
        sources = []
        for source in metric["sources"]:
            if source not in universal_sources:
                source_name = data_model["sources"][source]["name"]
                sources.append(f"[{source_name}]({metric_source_slug(data_model, metric, source)})")
        markdown += markdown_table_row(
            metric["name"], metric["description"], target, scales, tags, ", ".join(sorted(sources))
        )
    markdown += "\n"
    return markdown


def sources_table(data_model, universal_sources: list[str]) -> str:
    """Return the sources as Markdown table."""
    markdown = markdown_table_header("Name", "Description", "Metrics")
    for source_key, source in sorted(data_model["sources"].items(), key=lambda item: str(item[1]["name"])):
        source_name = f"[{source['name']}]({source['url']})" if "url" in source else source["name"]
        if source_key in universal_sources:
            metrics = "¹"
        else:
            metrics = ", ".join(
                [
                    f"[{metric['name']}]({metric_source_slug(data_model, metric, source_key)})"
                    for metric in data_model["metrics"].values()
                    if source_key in metric["sources"]
                ]
            )
        markdown += markdown_table_row(source_name, source["description"], metrics)
    markdown += "\n"
    return markdown


def metric_source_slug(data_model, metric, source) -> str:
    """Return a slug for the metric source combination."""
    source_name = data_model["sources"][source]["name"]
    return f"#{metric['name']} from {source_name}".lower().replace(" ", "-")


def metric_source_table(data_model, metric_key, source_key) -> str:
    """Return the metric source combination as Markdown table."""
    markdown = markdown_table_header("Parameter", "Type", "Values", "Default value", "Mandatory", "Help")
    for parameter in sorted(
        data_model["sources"][source_key]["parameters"].values(), key=lambda parameter: str(parameter["name"])
    ):
        if metric_key in parameter["metrics"]:
            name = parameter["name"]
            parameter_type = TYPE_DESCRIPTION[parameter["type"]]
            default_value = parameter["default_value"]
            if isinstance(default_value, list):
                if not default_value and parameter["type"] in ("single_choice", "multiple_choice"):
                    default_value = f"_all {parameter['short_name']}_"
                else:
                    default_value = ", ".join(default_value)
            if parameter["type"] in ("single_choice", "multiple_choice"):
                values = ", ".join(sorted(parameter["values"]))
            else:
                values = ""
            mandatory = "Yes" if parameter["mandatory"] else "No"
            help_url = markdown_link(parameter["help_url"]) if "help_url" in parameter else parameter.get("help", "")
            markdown += markdown_table_row(name, parameter_type, values, default_value, mandatory, help_url)
    markdown += "\n"
    return markdown


def metric_source_configuration_table(data_model, metric_key, source_key) -> str:
    """Return the metric source combination's configuration as Markdown table."""
    configurations = data_model["sources"][source_key].get("configuration", {}).values()
    relevant_configurations = [config for config in configurations if metric_key in config["metrics"]]
    if not relevant_configurations:
        return ""
    markdown = markdown_table_header("Configuration", "Value")
    for configuration in sorted(relevant_configurations, key=lambda config: str(config["name"])):
        name = configuration["name"]
        values = ", ".join(sorted(configuration["value"], key=lambda value: value.lower()))
        markdown += markdown_table_row(name, values)
    markdown += "\n"
    return markdown


def data_model_as_table(data_model) -> str:
    """Return the data model as Markdown table."""
    markdown = markdown_header("Quality-time metrics and sources")
    markdown += (
        "\nThis document lists all [metrics](#metrics) that *Quality-time* can measure and all "
        "[sources](#sources) that *Quality-time* can use to measure the metrics. For each "
        "[supported combination of metric and source](#supported-metric-source-combinations), it lists the "
        "parameters that can be used to configure the source.\n"
    )
    markdown += markdown_header("Metrics", 2)
    markdown += metrics_table(data_model, universal_sources := ["manual_number"])
    markdown += markdown_header("Sources", 2)
    markdown += sources_table(data_model, universal_sources)
    markdown += "¹) All metrics with the count or percentage scale can be measured using the 'Manual number' source.\n"
    markdown += markdown_header("Supported metric-source combinations", 2)
    for metric_key, metric in data_model["metrics"].items():
        for source_key in metric["sources"]:
            if source_key not in universal_sources:
                markdown += markdown_header(f"{metric['name']} from {data_model['sources'][source_key]['name']}", 3)
                markdown += metric_source_table(data_model, metric_key, source_key)
                markdown += metric_source_configuration_table(data_model, metric_key, source_key)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)  # Replace multiple consecutive empty lines with one empty line
    return re.sub(r"\n\n$", "\n", markdown)  # Remove final empty line


if __name__ == "__main__":
    data_model_md_path = pathlib.Path(__file__).resolve().parent.parent / "METRICS_AND_SOURCES.md"
    with data_model_md_path.open("w") as data_model_md:
        data_model_md.write(data_model_as_table(get_data_model()))
