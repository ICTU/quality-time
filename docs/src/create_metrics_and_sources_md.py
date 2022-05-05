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
    from external.data_model import DATA_MODEL_JSON  # pylint: disable=import-error,import-outside-toplevel

    return json.loads(DATA_MODEL_JSON)


def markdown_paragraph(text: str) -> str:
    """Return the text as Markdown paragraph."""
    return f"\n{text}\n\n"


def markdown_link(url: str, anchor: str = None) -> str:
    """Return a Markdown link."""
    anchor = anchor or url
    return f"[{anchor}]({url})"


def definition_list(term: str, *definitions: str) -> str:
    """Return a Markdown definition list."""
    definitions_markdown = "".join(f": {definition}\n" for definition in definitions if definition)
    return f"{term}\n{definitions_markdown}\n" if definitions_markdown else ""


def markdown_header(header: str, level: int = 1, index: bool = False) -> str:
    """Return a Markdown header."""
    index_preamble = f"\n```{{index}} {header}\n```\n\n" if index else ("\n" if level > 1 else "")
    return index_preamble + "#" * level + f" {header}\n\n"


def metric_sections(data_model, level) -> str:
    """Return the metrics as Markdown sections."""
    markdown = ""
    for metric in sorted(data_model["metrics"].values(), key=lambda item: str(item["name"])):
        markdown += metric_section(data_model, metric, level)
    return markdown


def metric_section(data_model, metric, level) -> str:
    """Return the metric as Markdown section."""
    markdown = markdown_header(metric["name"], level=level, index=True)
    markdown += markdown_paragraph(metric["description"])
    if metric.get("rationale"):
        markdown += markdown_paragraph(f"Why measure {decapitalize(metric['name'])}? {metric['rationale']}")
        if rationale_urls := metric.get("rationale_urls"):
            markdown += "```{seealso}\n"
            for url in rationale_urls:
                markdown += f"- {markdown_link(url)}\n"
            markdown += "```\n\n"
    markdown += definition_list("Default target", metric_target(metric))
    markdown += definition_list("Scales", *metric_scales(metric))
    markdown += definition_list("Default tags", *metric["tags"])
    markdown += "```{admonition} Supporting sources\n"
    for source in metric["sources"]:
        source_name = data_model["sources"][source]["name"]
        default = " (default)" if source == metric.get("default_source", "no default source") else ""
        markdown += f"- [{source_name}]({metric_source_slug(metric['name'], source_name)}){default}\n"
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


def source_sections(data_model, level) -> str:
    """Return the sources as Markdown sections."""
    markdown = ""
    for source_key, source in sorted(data_model["sources"].items(), key=lambda item: str(item[1]["name"])):
        markdown += source_section(data_model, source, source_key, level)
    return markdown


def source_section(data_model, source, source_key, level) -> str:
    """Return the source as Markdown section."""
    markdown = markdown_header(source["name"], level, index=True)
    markdown += markdown_paragraph(source["description"])
    markdown += "```{admonition} Supported metrics\n"
    metrics = [metric for metric in data_model["metrics"].values() if source_key in metric["sources"]]
    for metric in metrics:
        source_name = data_model["sources"][source_key]["name"]
        markdown += f"- [{metric['name']}]({metric_source_slug(metric['name'], source_name)})\n"
    markdown += "```\n\n"
    if "url" in source:
        markdown += f"```{{seealso}}\n{markdown_link(source['url'])}\n```\n\n"
    return markdown


def slugify(name) -> str:
    """Return a slugified version of the name."""
    return f'#{name.lower().replace(" ", "-").replace("(", "").replace(")", "")}'


def decapitalize(name: str) -> str:
    """Return the name starting with a lower case letter."""
    return name[0].lower() + name[1:]


def metric_source_slug(metric_name: str, source_name: str) -> str:
    """Return a slug for the metric source combination."""
    return slugify(f"{metric_name} from {source_name}")


def metric_source_section(data_model, metric_key: str, source_key: str) -> str:
    """Return the metric source combination as Markdown section."""
    source = data_model["sources"][source_key]
    source_name = source["name"]
    metric = data_model["metrics"][metric_key]
    metric_name = metric["name"]
    metric_link = f"[{metric_name.lower()}]({slugify(metric_name)})"
    source_link = f"[{source_name}]({slugify(source_name)})"
    markdown = markdown_paragraph(f"{source_link} can be used to measure {metric_link.lower()}.")
    if documentation := source.get("documentation", {}).get(metric_key):
        markdown += markdown_paragraph(documentation)
    parameters = [p for p in source["parameters"].values() if metric_key in p["metrics"]]
    for mandatory in True, False:
        markdown += parameter_paragraph(parameters, mandatory)
    return markdown


def parameter_paragraph(parameters: list[dict], mandatory: bool) -> str:
    """Return the parameters as Markdown paragraph."""
    markdown = ""
    parameters = [parameter for parameter in parameters if parameter["mandatory"] == mandatory]
    if parameters:
        markdown += markdown_header(f"{'Mandatory' if mandatory else 'Optional'} parameters", 4)
        sorted_parameters = sorted(parameters, key=lambda parameter: str(parameter["name"]))
        for parameter in sorted_parameters:
            markdown += parameter_description(parameter)
    return markdown


def parameter_description(parameter: dict) -> str:
    """Return the Markdown version of the parameter."""
    short_name = parameter["short_name"]
    if help_text := parameter.get("help", ""):
        help_text = " " + help_text
    if parameter["type"] in ("single_choice", "multiple_choice"):
        parameter_type = parameter["type"].replace("_", " ")
        values = ", ".join(sorted([f"`{value}`" for value in parameter["values"]]))
        values_text = f" This parameter is {parameter_type}. Possible {short_name} are: {values}."
    else:
        values_text = ""
    default_value = parameter["default_value"]
    if isinstance(default_value, list):
        if not default_value and parameter["type"] in ("single_choice", "multiple_choice"):
            default_value = [f"_all {short_name}_"]
        else:
            default_value = [f"`{value}`" for value in default_value]
    elif default_value:
        default_value = [f"`{default_value}`"]
    default_value_text = f" The default value is: {', '.join(sorted(default_value))}." if default_value else ""
    if help_url := parameter.get("help_url", ""):
        help_url = f"\n\n  ```{{seealso}}\n  {markdown_link(help_url)}\n  ```\n\n"
    return f"- **{parameter['name']}**.{help_text}{values_text}{default_value_text}\n{help_url}"


def metric_source_configuration_section(data_model, metric_key, source_key) -> str:
    """Return the metric source combination's configuration as Markdown section."""
    configurations = data_model["sources"][source_key].get("configuration", {}).values()
    relevant_configurations = [config for config in configurations if metric_key in config["metrics"]]
    if not relevant_configurations:
        return ""
    markdown = markdown_paragraph("Configurations:")
    for configuration in sorted(relevant_configurations, key=lambda config: str(config["name"])):
        markdown += f"- {configuration['name']}:\n"
        for value in sorted(configuration["value"], key=lambda value: str(value).lower()):
            markdown += f"  - {value}\n"
    markdown += "\n"
    return markdown


def data_model_as_table(data_model) -> str:
    """Return the data model as Markdown table."""
    markdown = markdown_paragraph(
        "This is an overview of all [metrics](#metrics) that *Quality-time* can measure and all "
        "[sources](#sources) that *Quality-time* can use to measure the metrics. For each "
        "[supported combination of metric and source](#metric-source-combinations), the parameters "
        "that can be used to configure the source are listed."
    )
    markdown += markdown_header("Metrics", 2)
    markdown += markdown_paragraph(
        "This is an overview of all the metrics that *Quality-time* can measure. For each metric, the "
        "default target, the supported scales, and the default tags are given. In addition, the sources that "
        "can be used to measure the metric are listed."
    )
    markdown += metric_sections(data_model, 3)
    markdown += markdown_header("Sources", 2)
    markdown += markdown_paragraph(
        "This is an overview of all the sources that *Quality-time* can use to measure metrics. For each source, "
        "the metrics that the source can measure are listed. Also, a link to the source's own documentation "
        "is provided."
    )
    markdown += source_sections(data_model, 3)
    markdown += markdown_header("Metric-source combinations", 2)
    markdown += markdown_paragraph(
        "This is an overview of all supported combinations of metrics and sources. For each combination of metric "
        "and source, the mandatory and optional parameters are listed that can be used to configure the source to "
        "measure the metric. If *Quality-time* needs to make certain assumptions about the source, for example which "
        "SonarQube rules to use to count long methods, then these assumptions are listed under 'configurations'."
    )
    for metric_key, metric in data_model["metrics"].items():
        for source_key in metric["sources"]:
            source_name = data_model["sources"][source_key]["name"]
            markdown += markdown_header(f"{metric['name']} from {source_name}", 3)
            markdown += metric_source_section(data_model, metric_key, source_key)
            markdown += metric_source_configuration_section(data_model, metric_key, source_key)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)  # Replace multiple consecutive empty lines with one empty line
    return re.sub(r"\n\n$", "\n", markdown)  # Remove final empty line


def main() -> None:
    """Convert the data model."""
    build_path = pathlib.Path(__file__).resolve().parent.parent / "build"
    build_path.mkdir(exist_ok=True)
    data_model_md_path = build_path / "metrics_and_sources.md"
    with data_model_md_path.open("w") as data_model_md:
        data_model_md.write(data_model_as_table(get_data_model()))


if __name__ == "__main__":
    main()
