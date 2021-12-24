"""OWASP ZAP source."""

from ..meta.source import Source
from ..parameters import (
    access_parameters,
    MultipleChoiceParameter,
    MultipleChoiceWithAdditionParameter,
    SingleChoiceParameter,
)


ALL_OWASP_ZAP_METRICS = ["security_warnings", "source_up_to_dateness", "source_version"]

OWASP_ZAP = Source(
    name="OWASP ZAP",
    description="The OWASP Zed Attack Proxy (ZAP) can help automatically find security vulnerabilities in web "
    "applications while the application is being developed and tested.",
    url="https://owasp.org/www-project-zap/",
    parameters=dict(
        alerts=SingleChoiceParameter(
            name="Count alert types or alert instances",
            short_name="count alert types or instances setting",
            help="Determine whether to count each alert type in the OWASP ZAP report as a security warning or to "
            "count each alert instance (URL).",
            default_value="alert instances",
            values=["alert types", "alert instances"],
            metrics=["security_warnings"],
        ),
        risks=MultipleChoiceParameter(
            name="Risks",
            help="If provided, only count security warnings with the selected risks.",
            placeholder="all risks",
            values=["informational", "low", "medium", "high"],
            api_values=dict(informational="0", low="1", medium="2", high="3"),
            metrics=["security_warnings"],
        ),
        variable_url_regexp=MultipleChoiceWithAdditionParameter(
            name="Parts of URLs to ignore (regular expressions)",
            short_name="parts of URLs to ignore",
            help="Parts of URLs to ignore can be specified by regular expression. The parts of URLs that match one or "
            "more of the regular expressions are removed. If, after applying the regular expressions, multiple "
            "warnings are the same only one is reported.",
            metrics=["security_warnings"],
        ),
        **access_parameters(ALL_OWASP_ZAP_METRICS, source_type="an OWASP ZAP report", source_type_format="XML")
    ),
    entities=dict(
        security_warnings=dict(
            name="security warning",
            attributes=[
                dict(name="Warning", key="name"),
                dict(
                    name="Risk (Confidence)",
                    key="risk",
                    color={
                        "High (Low)": "negative",
                        "High (Medium)": "negative",
                        "High (High)": "negative",
                        "Medium (Low)": "warning",
                        "Medium (Medium)": "warning",
                        "Medium (High)": "warning",
                    },
                ),
                dict(name="Description"),
                dict(name="Location", url="uri"),
            ],
        ),
    ),
)
