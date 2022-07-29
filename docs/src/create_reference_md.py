"""Script to convert the data model in a Markdown file."""

import pathlib
import re

from shared_data_model import DATA_MODEL
from shared_data_model.meta import Metric, NamedModel, Parameter, Source, Subject

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


def get_model_name(model: NamedModel) -> str:
    """Return the name of the model."""
    # This function could easily be a lambda, but then we can't add type information
    return model.name


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


def subject_sections(level: int) -> str:
    """Return the subjects as Markdown sections."""
    markdown = ""
    for subject in sorted(DATA_MODEL.subjects.values(), key=get_model_name):
        markdown += subject_section(subject, level)
    return markdown


def subject_section(subject: Subject, level: int) -> str:
    """Return the subject as Markdown section."""
    markdown = markdown_header(subject.name, level=level, index=True)
    markdown += markdown_paragraph(subject.description)
    markdown += "```{admonition} Supporting metrics\n"
    for metric in subject.metrics:
        metric_name = DATA_MODEL.metrics[metric].name
        markdown += f"- [{metric_name}]({slugify(metric_name)})\n"
    markdown += "```\n"
    return markdown


def metric_sections(level: int) -> str:
    """Return the metrics as Markdown sections."""
    markdown = ""
    for metric_key, metric in sorted(DATA_MODEL.metrics.items(), key=lambda item: get_model_name(item[1])):
        markdown += metric_section(metric_key, metric, level)
    return markdown


def metric_section(metric_key: str, metric: Metric, level: int) -> str:
    """Return the metric as Markdown section."""
    markdown = markdown_header(metric.name, level=level, index=True)
    markdown += markdown_paragraph(metric.description)
    markdown += markdown_paragraph(f"*Why measure {decapitalize(metric.name)}?* {metric.rationale}")
    if rationale_urls := metric.rationale_urls:
        markdown += see_also_links(rationale_urls)
    if explanation := metric.explanation:
        markdown += markdown_paragraph(f"*More information* {explanation}")
        if explanation_urls := metric.explanation_urls:  # pragma: no branch
            markdown += see_also_links(explanation_urls)
    markdown += definition_list("Default target", metric_target(metric))
    markdown += definition_list("Scales", *metric_scales(metric))
    markdown += definition_list("Default tags", *metric.tags)
    markdown += "```{admonition} Supported subjects\n"
    subjects = [subject for subject in DATA_MODEL.subjects.values() if metric_key in subject.metrics]
    for subject in subjects:
        markdown += f"- [{subject.name}]({slugify(subject.name)})\n"
    markdown += "```\n\n"
    markdown += "```{admonition} Supporting sources\n"
    for source in metric.sources:
        source_name = DATA_MODEL.sources[source].name
        markdown += f"- [{source_name}]({metric_source_slug(metric.name, source_name)})\n"
    markdown += "```\n"
    return markdown


def see_also_links(urls: list[str]) -> str:
    """Return a see also section with a list of URLs."""
    markdown = "```{seealso}\n"
    for url in urls:
        markdown += f"1. {markdown_link(url)}\n"
    markdown += "```\n\n"
    return markdown


def metric_target(metric: Metric) -> str:
    """Return the metric target."""
    direction = {"<": "≦", ">": "≧"}[metric.direction]
    if metric.default_scale == "percentage":
        unit = "% of the " + metric.unit
    elif metric.default_scale == "version_number":
        unit = ""
    else:
        unit = " " + metric.unit
    return f"{direction} {metric.target}{unit}"


def metric_scales(metric: Metric) -> list[str]:
    """Return the scales of the metric."""
    if len(metric.scales) == 1:
        return [metric.default_scale]
    return [f"{scale} (default)" if scale == metric.default_scale else scale for scale in sorted(metric.scales)]


def source_sections(level: int) -> str:
    """Return the sources as Markdown sections."""
    markdown = ""
    for source_key, source in sorted(DATA_MODEL.sources.items(), key=lambda item: get_model_name(item[1])):
        markdown += source_section(source, source_key, level)
    return markdown


def source_section(source: Source, source_key: str, level: int) -> str:
    """Return the source as Markdown section."""
    markdown = markdown_header(source.name, level, index=True)
    markdown += markdown_paragraph(source.description)
    markdown += "```{admonition} Supported metrics\n"
    metrics = [metric for metric in DATA_MODEL.metrics.values() if source_key in metric.sources]
    for metric in metrics:
        source_name = DATA_MODEL.sources[source_key].name
        markdown += f"- [{metric.name}]({metric_source_slug(metric.name, source_name)})\n"
    markdown += "```\n\n"
    if source.url:
        markdown += f"```{{seealso}}\n{markdown_link(source.url)}\n```\n\n"
    return markdown


def slugify(name: str) -> str:
    """Return a slugified version of the name."""
    return f'#{name.lower().replace(" ", "-").replace("(", "").replace(")", "")}'


def decapitalize(name: str) -> str:
    """Return the name starting with a lower case letter."""
    return name[0].lower() + name[1:]


def metric_source_slug(metric_name: str, source_name: str) -> str:
    """Return a slug for the metric source combination."""
    return slugify(f"{metric_name} from {source_name}")


def metric_source_section(metric_key: str, source_key: str) -> str:
    """Return the metric source combination as Markdown section."""
    source = DATA_MODEL.sources[source_key]
    metric = DATA_MODEL.metrics[metric_key]
    metric_link = f"[{metric.name.lower()}]({slugify(metric.name)})"
    source_link = f"[{source.name}]({slugify(source.name)})"
    markdown = markdown_paragraph(f"{source_link} can be used to measure {metric_link.lower()}.")
    if documentation := (source.documentation and source.documentation.get(metric_key)):
        markdown += markdown_paragraph(documentation)
    parameters = [p for p in source.parameters.values() if metric_key in p.metrics]
    for mandatory in True, False:
        markdown += parameter_paragraph(parameters, mandatory)
    return markdown


def parameter_paragraph(parameters: list[Parameter], mandatory: bool) -> str:
    """Return the parameters as Markdown paragraph."""
    markdown = ""
    parameters = [parameter for parameter in parameters if parameter.mandatory == mandatory]
    if parameters:
        markdown += markdown_header(f"{'Mandatory' if mandatory else 'Optional'} parameters", 4)
        sorted_parameters = sorted(parameters, key=get_model_name)
        for parameter in sorted_parameters:
            markdown += parameter_description(parameter)
    return markdown


def parameter_description(parameter: Parameter) -> str:
    """Return the Markdown version of the parameter."""
    short_name = parameter.short_name
    help_text = " " + parameter.help if parameter.help else ""
    if parameter.type in ("single_choice", "multiple_choice"):
        parameter_type = parameter.type.replace("_", " ")
        values = ", ".join(sorted([f"`{value}`" for value in parameter.values or []]))
        values_text = f" This parameter is {parameter_type}. Possible {short_name} are: {values}."
    else:
        values_text = ""
    default_value = parameter.default_value
    if isinstance(default_value, list):
        if not default_value and parameter.type in ("single_choice", "multiple_choice"):
            default_value = [f"_all {short_name}_"]
        else:
            default_value = [f"`{value}`" for value in default_value]
    elif default_value:
        default_value = [f"`{default_value}`"]
    default_value_text = f" The default value is: {', '.join(sorted(default_value))}." if default_value else ""
    if parameter.help_url:
        help_url = f"\n\n  ```{{seealso}}\n  {markdown_link(parameter.help_url)}\n  ```\n\n"
    else:
        help_url = ""
    return f"- **{parameter.name}**.{help_text}{values_text}{default_value_text}\n{help_url}"


def metric_source_configuration_section(metric_key: str, source_key: str) -> str:
    """Return the metric source combination's configuration as Markdown section."""
    configurations = DATA_MODEL.sources[source_key].configuration.values()
    relevant_configurations = [config for config in configurations if metric_key in config.metrics]
    if not relevant_configurations:
        return ""
    markdown = markdown_paragraph("Configurations:")
    for configuration in sorted(relevant_configurations, key=get_model_name):
        markdown += f"- {configuration.name}:\n"
        for value in sorted(configuration.value, key=lambda value: str(value).lower()):
            markdown += f"  - {value}\n"
    markdown += "\n"
    return markdown


def data_model_as_table() -> str:
    """Return the data model as Markdown table."""
    markdown = markdown_paragraph(
        "This is an overview of all [subjects](#subjects) that *Quality-time* can measure, all [metrics](#metrics) "
        "that *Quality-time* can use to measure subjects, and all [sources](#sources) that *Quality-time* can use to "
        "collect data from to measure the metrics. For each supported "
        "[combination of metric and source](#metric-source-combinations), the parameters that can be used to configure "
        "the source are listed."
    )
    markdown += markdown_header("Subjects", 2)
    markdown += markdown_paragraph(
        "This is an overview of all the subjects that *Quality-time* can measure. For each subject, the "
        "metrics that can be used to measure the subject are listed."
    )
    markdown += subject_sections(3)
    markdown += markdown_header("Metrics", 2)
    markdown += markdown_paragraph(
        "This is an overview of all the metrics that *Quality-time* can use to measure subjects. For each metric, the "
        "default target, the supported scales, and the default tags are given. In addition, the sources that "
        "can be used to collect data from to measure the metric are listed."
    )
    markdown += metric_sections(3)
    markdown += markdown_header("Sources", 2)
    markdown += markdown_paragraph(
        "This is an overview of all the sources that *Quality-time* can use to measure metrics. For each source, "
        "the metrics that the source can measure are listed. Also, a link to the source's own documentation "
        "is provided."
    )
    markdown += source_sections(3)
    markdown += markdown_header("Metric-source combinations", 2)
    markdown += markdown_paragraph(
        "This is an overview of all supported combinations of metrics and sources. For each combination of metric "
        "and source, the mandatory and optional parameters are listed that can be used to configure the source to "
        "measure the metric. If *Quality-time* needs to make certain assumptions about the source, for example which "
        "SonarQube rules to use to count long methods, then these assumptions are listed under 'configurations'."
    )
    for metric_key, metric in DATA_MODEL.metrics.items():
        for source_key in metric.sources:
            source_name = DATA_MODEL.sources[source_key].name
            markdown += markdown_header(f"{metric.name} from {source_name}", 3)
            markdown += metric_source_section(metric_key, source_key)
            markdown += metric_source_configuration_section(metric_key, source_key)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)  # Replace multiple consecutive empty lines with one empty line
    return re.sub(r"\n\n$", "\n", markdown)  # Remove final empty line


def main() -> None:
    """Convert the data model."""
    build_path = pathlib.Path(__file__).resolve().parent.parent / "build"
    build_path.mkdir(exist_ok=True)
    data_model_md_path = build_path / "reference.md"
    with data_model_md_path.open("w") as data_model_md:
        data_model_md.write(data_model_as_table())


if __name__ == "__main__":  # pragma: no cover
    main()
