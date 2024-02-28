import PropTypes from 'prop-types';
import { Segment } from '../semantic_ui_react_wrappers';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { Subjects } from '../subject/Subjects';
import { CommentSegment } from '../widgets/CommentSegment';
import { add_report, copy_report } from '../api/report';
import { ReportsOverviewTitle } from './ReportsOverviewTitle';
import { AddButton, CopyButton } from '../widgets/Button';
import { report_options } from '../widgets/menu_options';
import { getReportsTags } from '../utils';
import {
    datesPropType,
    optionalDatePropType,
    reportsOverviewPropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
} from '../sharedPropTypes';
import { ReportsOverviewErrorMessage } from './ReportErrorMessage';
import { ReportsOverviewDashboard } from './ReportsOverviewDashboard';


function ReportsOverviewButtonRow({ reload, reports }) {
    return (
        <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
            <Segment basic>
                <AddButton
                    item_type={"report"}
                    onClick={() => add_report(reload)}
                />
                <CopyButton
                    item_type={"report"}
                    get_options={() => report_options(reports)}
                    onChange={(source_report_uuid) => copy_report(source_report_uuid, reload)}
                />
            </Segment>
        }
        />
    )
}
ReportsOverviewButtonRow.propTypes = {
    reload: PropTypes.func,
    reports: reportsPropType
}

export function ReportsOverview(
    {
        changed_fields,
        dates,
        handleSort,
        measurements,
        openReport,
        reload,
        reports,
        report_date,
        reports_overview,
        settings
    }
) {
    if (reports.length === 0 && report_date !== null) {
        return <ReportsOverviewErrorMessage reportDate={report_date} />
    }
    // Sort measurements in reverse order so that if there multiple measurements on a day, we find the most recent one:
    const reversedMeasurements = measurements.slice().sort((m1, m2) => m1.start < m2.start ? 1 : -1)
    return (
        <div id="dashboard">
            <ReportsOverviewTitle reports_overview={reports_overview} reload={reload} settings={settings} />
            <CommentSegment comment={reports_overview.comment} />
            <ReportsOverviewDashboard
                dates={dates}
                layout={reports_overview.layout ?? []}
                measurements={reversedMeasurements}
                onClickTag={(tag) => {
                    // If there are hidden tags (hiddenTags.length > 0), show the hidden tags.
                    // Otherwise, hide all tags in all reports except the one clicked on.
                    const tagsToToggle = settings.hiddenTags.value.length > 0 ? settings.hiddenTags.value : getReportsTags(reports)
                    settings.hiddenTags.toggle(...tagsToToggle.filter((visibleTag) => visibleTag !== tag))
                }}
                openReport={openReport}
                reload={reload}
                reports={reports}
                settings={settings}
            />
            <Subjects
                atReportsOverview={true}
                changed_fields={changed_fields}
                dates={dates}
                handleSort={handleSort}
                measurements={measurements}
                reload={reload}
                reportsToShow={reports}
                report_date={report_date}
                reports={reports}
                settings={settings}
            />
            <ReportsOverviewButtonRow reload={reload} reports={reports} />
        </div>
    )
}
ReportsOverview.propTypes = {
    changed_fields: stringsPropType,
    dates: datesPropType,
    handleSort: PropTypes.func,
    measurements: PropTypes.array,
    reports: reportsPropType,
    openReport: PropTypes.func,
    reload: PropTypes.func,
    report_date: optionalDatePropType,
    reports_overview: reportsOverviewPropType,
    settings: settingsPropType
}
