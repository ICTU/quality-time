"""Checkmarx CxSAST source."""

from ..meta.source import Source
from ..parameters import access_parameters, Severities, StringParameter


ALL_CXSAST_METRICS = ["security_warnings", "source_up_to_dateness", "source_version"]

CXSAST = Source(
    name="Checkmarx CxSAST",
    description="Static analysis software to identify security vulnerabilities in both custom code and open source "
    "components.",
    url="https://checkmarx.com/glossary/static-application-security-testing-sast/",
    parameters=dict(
        project=StringParameter(
            name="Project (name or id)",
            short_name="project",
            mandatory=True,
            metrics=["security_warnings", "source_up_to_dateness"],
        ),
        severities=Severities(values=["info", "low", "medium", "high"]),
        **access_parameters(
            ALL_CXSAST_METRICS,
            include=dict(private_token=False, landing_url=False),
            kwargs=dict(
                url=dict(
                    help="URL of the Checkmarx instance, with port if necessary, but without path. For example "
                    "'https://checkmarx.example.org'."
                ),
                username=dict(mandatory=True),
                password=dict(mandatory=True),
            ),
        )
    ),
)
