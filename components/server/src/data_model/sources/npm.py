"""npm source."""

from ..meta.source import Source
from ..parameters import access_parameters


NPM = Source(
    name="npm",
    description="npm is a package manager for the JavaScript programming language.",
    url="https://docs.npmjs.com/",
    parameters=access_parameters(
        ["dependencies"],
        source_type="npm 'outdated' report",
        source_type_format="JSON",
        kwargs=dict(url=dict(help_url="https://docs.npmjs.com/cli-commands/outdated.html")),
    ),
    entities=dict(
        dependencies=dict(
            name="dependency",
            name_plural="dependencies",
            attributes=[
                dict(name="Package", key="name"),
                dict(name="Current version", key="current"),
                dict(name="Wanted version", key="wanted"),
                dict(name="Latest version", key="latest"),
            ],
        )
    ),
)
