import { Divider, Paper } from "@mui/material"
import { func } from "prop-types"

import { PageHeader } from "../dashboard/PageHeader"
import {
    datePropType,
    datesPropType,
    measurementsPropType,
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
import { WarningMessage } from "../widgets/WarningMessage"
import { ReportDashboard } from "./ReportDashboard"
import { ReportTitle } from "./ReportTitle"

export function Report({
    changedFields,
    dates,
    handleSort,
    lastUpdate,
    measurements,
    openReportsOverview,
    reload,
    report,
    reportDate,
    reports,
    settings,
}) {
    function navigateToSubject(event, subjectUuid) {
        event.preventDefault()
        const element = document.getElementById(subjectUuid)
        if (element) {
            element.scrollIntoView()
            globalThis.scrollBy(0, 163) // Correct for menubar and subject title margin
        }
    }

    if (!report) {
        return (
            <WarningMessage title="Report not found">
                {reportDate ? `Sorry, this report didn't exist at ${reportDate}` : "Sorry, this report doesn't exist"}
            </WarningMessage>
        )
    }
    // Sort measurements in reverse order so that if there multiple measurements on a day, we find the most recent one:
    const reversedMeasurements = measurements.slice().sort((m1, m2) => (m1.start < m2.start ? 1 : -1))
    return (
        <div id="dashboard">
            <PageHeader lastUpdate={lastUpdate} report={report} reportDate={reportDate} />
            <Paper elevation={5} sx={{ marginTop: "20px" }}>
                <ReportTitle
                    openReportsOverview={openReportsOverview}
                    reload={reload}
                    report={report}
                    settings={settings}
                />
                <CommentSegment comment={report.comment} />
                <Divider sx={{ padding: "0px" }} />
                <ReportDashboard
                    dates={dates}
                    measurements={reversedMeasurements}
                    onClick={(e, s) => navigateToSubject(e, s)}
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
            </Paper>
            <Subjects
                atReportsOverview={false}
                changedFields={changedFields}
                dates={dates}
                handleSort={handleSort}
                measurements={measurements}
                reload={reload}
                reports={reports}
                reportsToShow={[report]}
                reportDate={reportDate}
                settings={settings}
            />
            <SubjectsButtonRow reload={reload} report={report} reports={reports} settings={settings} />
        </div>
    )
}
Report.propTypes = {
    changedFields: stringsPropType,
    dates: datesPropType,
    handleSort: func,
    lastUpdate: datePropType,
    measurements: measurementsPropType,
    openReportsOverview: func,
    reload: func,
    report: reportPropType,
    reportDate: optionalDatePropType,
    reports: reportsPropType,
    settings: settingsPropType,
}
