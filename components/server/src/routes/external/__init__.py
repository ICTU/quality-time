"""External routes."""

from .auth import login, logout, get_public_key
from .changelog import (
    get_changelog,
    get_metric_changelog,
    get_subject_changelog,
    get_source_changelog,
    get_report_changelog,
)
from .datamodel import get_data_model
from .documentation import get_api
from .logo import get_logo
from .measurement import get_measurements, set_entity_attribute, stream_nr_measurements
from .metric import delete_metric, post_metric_attribute, post_metric_copy, post_metric_new, post_move_metric
from .notification import (
    delete_notification_destination,
    post_new_notification_destination,
    post_notification_destination_attributes,
)
from .report import (
    delete_report,
    export_report_as_json,
    export_report_as_pdf,
    get_report,
    post_report_import,
    post_report_copy,
    post_report_attribute,
    post_report_issue_tracker_attribute,
    post_report_new,
)
from .reports_overview import get_reports_overview, get_reports, post_reports_overview_attribute
from .server import get_server, QUALITY_TIME_VERSION
from .source import (
    delete_source,
    post_move_source,
    post_source_attribute,
    post_source_copy,
    post_source_new,
    post_source_parameter,
)
from .subject import (
    delete_subject,
    post_move_subject,
    post_new_subject,
    post_subject_attribute,
    post_subject_copy,
    get_subject_measurements,
)
