import { array, func } from "prop-types"

import { ExportCard } from "../dashboard/ExportCard"
import {
    datePropType,
    datesPropType,
    optionalDatePropType,
    reportPropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
} from "../sharedPropTypes"
import { Subjects } from "../subject/Subjects"
import { SubjectsButtonRow } from "../subject/SubjectsButtonRow"
import { getReportTags } from "../utils"
import { CommentSegment } from "../widgets/CommentSegment"
import { ReportDashboard } from "./ReportDashboard"
import { ReportErrorMessage } from "./ReportErrorMessage"
import { ReportTitle } from "./ReportTitle"

export function Report({
    changed_fields,
    dates,
    handleSort,
    lastUpdate,
    measurements,
    openReportsOverview,
    reload,
    report,
    report_date,
    reports,
    settings,
}) {
    function navigate_to_subject(event, subject_uuid) {
        event.preventDefault()
        const element = document.getElementById(subject_uuid)
        if (element) {
            element.scrollIntoView()
            window.scrollBy(0, 163) // Correct for menubar and subject title margin
        }
    }

    if (!report) {
        return <ReportErrorMessage reportDate={report_date} />
    }
    // Sort measurements in reverse order so that if there multiple measurements on a day, we find the most recent one:
    const reversedMeasurements = measurements.slice().sort((m1, m2) => (m1.start < m2.start ? 1 : -1))
    return (
        <div id="dashboard">
            <div className="reportHeader">
                <ReportTitle
                    openReportsOverview={openReportsOverview}
                    report={report}
                    changed_fields={changed_fields}
                    reload={reload}
                    report_date={report_date}
                    reports={reports}
                    settings={settings}
                />
                <ExportCard lastUpdate={lastUpdate} report={report} reportDate={report_date} />
            </div>
            <CommentSegment comment={report.comment} />
            <ReportDashboard
                dates={dates}
                measurements={reversedMeasurements}
                onClick={(e, s) => navigate_to_subject(e, s)}
                onClickTag={(tag) => {
                    // If there are hidden tags (hiddenTags.length > 0), show the hidden tags.
                    // Otherwise, hide all tags in this report except the one clicked on.
                    const tagsToToggle =
                        settings.hiddenTags.value.length > 0 ? settings.hiddenTags.value : getReportTags(report)
                    settings.hiddenTags.toggle(...tagsToToggle.filter((visibleTag) => visibleTag !== tag))
                }}
                report={report}
                reload={reload}
                settings={settings}
            />
            <Subjects
                atReportsOverview={false}
                changed_fields={changed_fields}
                dates={dates}
                handleSort={handleSort}
                measurements={measurements}
                reload={reload}
                reports={reports}
                reportsToShow={[report]}
                report_date={report_date}
                settings={settings}
            />
            <SubjectsButtonRow reload={reload} report={report} reports={reports} settings={settings} />
        </div>
    )
}
Report.propTypes = {
    changed_fields: stringsPropType,
    dates: datesPropType,
    handleSort: func,
    lastUpdate: datePropType,
    measurements: array,
    openReportsOverview: func,
    reload: func,
    report: reportPropType,
    report_date: optionalDatePropType,
    reports: reportsPropType,
    settings: settingsPropType,
}
