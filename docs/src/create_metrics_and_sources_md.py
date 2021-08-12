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


def get_data_model():
    """Return the data model."""
    module_dir = pathlib.Path(__file__).resolve().parent
    server_src_path = module_dir.parent.parent / "components" / "server" / "src"
    sys.path.insert(0, str(server_src_path))
    from data_model import DATA_MODEL_JSON  # pylint: disable=import-error,import-outside-toplevel

    return json.loads(DATA_MODEL_JSON)


def markdown_link(url: str, anchor: str = None) -> str:
    """Return a Markdown link."""
    anchor = anchor or url
    return f"[{anchor}]({url})"


def definition_list(term: str, *definitions: str) -> str:
    """Return a Markdown definition list."""
    definitions_markdown = "".join(f": {definition}\n" for definition in definitions if definition)
    return f"{term}\n{definitions_markdown}\n" if definitions_markdown else ""


def markdown_header(header: str, level: int = 1) -> str:
    """Return a Markdown header."""
    return ("\n" if level > 1 else "") + "#" * level + f" {header}\n\n"


def metric_sections(data_model, universal_sources: list[str], level) -> str:
    """Return the metrics as Markdown sections."""
    markdown = ""
    for metric in sorted(data_model["metrics"].values(), key=lambda item: str(item["name"])):
        markdown += metric_section(data_model, metric, universal_sources, level)
    return markdown


def metric_section(data_model, metric, universal_sources: list[str], level) -> str:
    """Return the metric as Markdown section."""
    markdown = markdown_header(metric["name"], level=level)
    markdown += f'\n{metric["description"]}\n\n'
    markdown += definition_list("Default target", metric_target(metric))
    markdown += definition_list("Scales", *metric_scales(metric))
    markdown += definition_list("Default tags", *metric["tags"])
    markdown += "```{admonition} Supporting sources\n"
    for source in metric["sources"]:
        if source not in universal_sources:
            source_name = data_model["sources"][source]["name"]
            markdown += f"- [{source_name}]({metric_source_slug(data_model, metric, source)})\n"
    markdown += "```\n"
    return markdown


def metric_target(metric) -> str:
    """Return the metric target."""
    direction = {"<": "≦", ">": "≧"}[metric["direction"]]
    if metric["default_scale"] == "percentage":
        unit = "% of the " + metric["unit"]
    elif metric["default_scale"] == "version_number":
        unit = ""
    else:
        unit = " " + metric["unit"]
    return f"{direction} {metric['target']}{unit}"


def metric_scales(metric) -> list[str]:
    """Return the scales of the metric."""
    if len(metric["scales"]) == 1:
        return [metric["default_scale"]]
    return [f"{scale} (default)" if scale == metric["default_scale"] else scale for scale in sorted(metric["scales"])]


def source_sections(data_model, universal_sources: list[str], level) -> str:
    """Return the sources as Markdown sections."""
    markdown = ""
    for source_key, source in sorted(data_model["sources"].items(), key=lambda item: str(item[1]["name"])):
        markdown += source_section(data_model, source, source_key, universal_sources, level)
    return markdown


def source_section(data_model, source, source_key, universal_sources: list[str], level) -> str:
    """Return the source as Markdown section."""
    source_name = f"[{source['name']}]({source['url']})" if "url" in source else source["name"]
    markdown = markdown_header(source_name, level)
    markdown += f'\n{source["description"]}\n\n'
    markdown += "```{admonition} Supported metrics\n"
    if source_key in universal_sources:
        markdown += "All metrics with the count or percentage scale can be measured with this source).\n"
    else:
        metrics = [metric for metric in data_model["metrics"].values() if source_key in metric["sources"]]
        for metric in metrics:
            markdown += f"- [{metric['name']}]({metric_source_slug(data_model, metric, source_key)})\n"
    markdown += "```\n"
    return markdown


def slugify(name) -> str:
    """Return a slugified version of the name."""
    return name.lower().replace(" ", "-").replace("(", "").replace(")", "")


def metric_source_slug(data_model, metric, source) -> str:
    """Return a slug for the metric source combination."""
    metric_name, source_name = metric["name"], data_model["sources"][source]["name"]
    return slugify(f"#{metric_name} from {source_name}")


def metric_slug(metric) -> str:
    """Return a slug for the metric."""
    metric_name = metric["name"]
    return slugify(f"#{metric_name}")


def source_slug(data_model, source) -> str:
    """Return a slug for the source."""
    source_name = data_model["sources"][source]["name"]
    return slugify(f"#{source_name}")


def metric_source_section(data_model, metric_key, source_key, level) -> str:
    """Return the metric source combination as Markdown section."""
    markdown = ""
    parameters = data_model["sources"][source_key]["parameters"].values()
    for parameter in sorted(parameters, key=lambda parameter: str(parameter["name"])):
        if metric_key not in parameter["metrics"]:
            continue
        markdown += markdown_header(parameter["name"], level)
        markdown += definition_list("Type", TYPE_DESCRIPTION[parameter["type"]])
        if parameter["type"] in ("single_choice", "multiple_choice"):
            markdown += definition_list("Values", *sorted(parameter["values"]))
        default_value = parameter["default_value"]
        if isinstance(default_value, list):
            if not default_value and parameter["type"] in ("single_choice", "multiple_choice"):
                default_value = [f"_all {parameter['short_name']}_"]
        elif default_value:
            default_value = [default_value]
        markdown += definition_list("Default value", *default_value)
        markdown += definition_list("Mandatory", "Yes" if parameter["mandatory"] else "No")
        help_markdown = markdown_link(parameter["help_url"]) if "help_url" in parameter else parameter.get("help", "")
        markdown += definition_list("Help", help_markdown)
    return markdown


def metric_source_configuration_section(data_model, metric_key, source_key, level) -> str:
    """Return the metric source combination's configuration as Markdown section."""
    configurations = data_model["sources"][source_key].get("configuration", {}).values()
    relevant_configurations = [config for config in configurations if metric_key in config["metrics"]]
    if not relevant_configurations:
        return ""
    markdown = markdown_header("Configurations", level)
    for configuration in sorted(relevant_configurations, key=lambda config: str(config["name"])):
        values = sorted(configuration["value"], key=lambda value: str(value).lower())
        markdown += definition_list(configuration["name"], *values)
    markdown += "\n"
    return markdown


def data_model_as_table(data_model) -> str:
    """Return the data model as Markdown table."""
    markdown = markdown_header("*Quality-time* metrics and sources")
    markdown += (
        "\nThis document lists all [metrics](#metrics) that *Quality-time* can measure and all "
        "[sources](#sources) that *Quality-time* can use to measure the metrics. For each "
        "[supported combination of metric and source](#supported-metric-source-combinations), it lists the "
        "parameters that can be used to configure the source.\n"
    )
    markdown += markdown_header("Metrics", 2)
    markdown += metric_sections(data_model, universal_sources := ["manual_number"], 3)
    markdown += markdown_header("Sources", 2)
    markdown += source_sections(data_model, universal_sources, 3)
    markdown += markdown_header("Supported metric-source combinations", 2)
    for metric_key, metric in data_model["metrics"].items():
        for source_key in metric["sources"]:
            if source_key not in universal_sources:
                metric_link = f"[{metric['name']}]({metric_slug(metric)})"
                source_link = f"[{data_model['sources'][source_key]['name']}]({source_slug(data_model, source_key)})"
                markdown += markdown_header(f"{metric_link} from {source_link}", 3)
                markdown += metric_source_section(data_model, metric_key, source_key, 4)
                markdown += metric_source_configuration_section(data_model, metric_key, source_key, 4)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)  # Replace multiple consecutive empty lines with one empty line
    return re.sub(r"\n\n$", "\n", markdown)  # Remove final empty line


if __name__ == "__main__":
    data_model_md_path = pathlib.Path(__file__).resolve().parent.parent / "source" / "metrics_and_sources.md"
    with data_model_md_path.open("w") as data_model_md:
        data_model_md.write(data_model_as_table(get_data_model()))
