"""pip source."""

from ..meta.source import Source
from ..parameters import access_parameters


PIP = Source(
    name="pip",
    description="pip is the package installer for Python. You can use pip to install packages from the Python Package "
    "Index and other indexes.",
    url="https://pip.pypa.io/en/stable/",
    parameters=access_parameters(
        ["dependencies"],
        source_type="pip 'outdated' report",
        source_type_format="JSON",
        kwargs=dict(url=dict(help_url="https://pip.pypa.io/en/stable/reference/pip_list/")),
    ),
    entities=dict(
        dependencies=dict(
            name="dependency",
            name_plural="dependencies",
            attributes=[
                dict(name="Package", key="name", url="homepage"),
                dict(name="Current version", key="version"),
                dict(name="Latest version", key="latest"),
            ],
        ),
    ),
)
