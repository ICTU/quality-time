import { Box } from "@mui/material"
import { func } from "prop-types"

import { addReport, copyReport } from "../api/report"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import { PageHeader } from "../dashboard/PageHeader"
import {
    datePropType,
    datesPropType,
    measurementsPropType,
    optionalDatePropType,
    reportsOverviewPropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
} from "../sharedPropTypes"
import { Subjects } from "../subject/Subjects"
import { getReportsTags } from "../utils"
import { ButtonRow } from "../widgets/ButtonRow"
import { AddButton } from "../widgets/buttons/AddButton"
import { CopyButton } from "../widgets/buttons/CopyButton"
import { ReportUploadButton } from "../widgets/buttons/ReportUploadButton"
import { CommentSegment } from "../widgets/CommentSegment"
import { reportOptions } from "../widgets/menu_options"
import { WarningMessage } from "../widgets/WarningMessage"
import { ReportsOverviewDashboard } from "./ReportsOverviewDashboard"
import { ReportsOverviewTitle } from "./ReportsOverviewTitle"

function ReportsOverviewButtonRow({ reload, reports }) {
    return (
        <ReadOnlyOrEditable
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            editableComponent={
                <Box sx={{ paddingTop: "50px" }}>
                    <ButtonRow>
                        <AddButton itemType="report" onClick={() => addReport(reload)} />
                        <CopyButton
                            itemType="report"
                            getOptions={() => reportOptions(reports)}
                            onChange={(reportUuid) => copyReport(reportUuid, reload)}
                        />
                        <ReportUploadButton reload={reload} />
                    </ButtonRow>
                </Box>
            }
        />
    )
}
ReportsOverviewButtonRow.propTypes = {
    reload: func,
    reports: reportsPropType,
}

export function ReportsOverview({
    changedFields,
    dates,
    handleSort,
    lastUpdate,
    measurements,
    openReport,
    reload,
    reports,
    reportDate,
    reportsOverview,
    settings,
}) {
    if (reports.length === 0 && reportDate !== null) {
        return <WarningMessage title="No reports found">{`Sorry, no reports existed at ${reportDate}`}</WarningMessage>
    }
    // Sort measurements in reverse order so that if there multiple measurements on a day, we find the most recent one:
    const reversedMeasurements = measurements.slice().sort((m1, m2) => (m1.start < m2.start ? 1 : -1))
    return (
        <div id="dashboard">
            <PageHeader lastUpdate={lastUpdate} reportDate={reportDate} />
            <ReportsOverviewTitle reportsOverview={reportsOverview} reload={reload} settings={settings} />
            <CommentSegment comment={reportsOverview.comment} />
            <ReportsOverviewDashboard
                dates={dates}
                layout={reportsOverview.layout ?? []}
                measurements={reversedMeasurements}
                onClickTag={(tag) => {
                    // If there are hidden tags (hiddenTags.length > 0), show the hidden tags.
                    // Otherwise, hide all tags in all reports except the one clicked on.
                    const tagsToToggle =
                        settings.hiddenTags.value.length > 0 ? settings.hiddenTags.value : getReportsTags(reports)
                    settings.hiddenTags.toggle(...tagsToToggle.filter((visibleTag) => visibleTag !== tag))
                }}
                openReport={openReport}
                reload={reload}
                reports={reports}
                settings={settings}
            />
            <Subjects
                atReportsOverview={true}
                changedFields={changedFields}
                dates={dates}
                handleSort={handleSort}
                measurements={measurements}
                reload={reload}
                reportsToShow={reports}
                reportDate={reportDate}
                reports={reports}
                settings={settings}
            />
            <ReportsOverviewButtonRow reload={reload} reports={reports} />
        </div>
    )
}
ReportsOverview.propTypes = {
    changedFields: stringsPropType,
    dates: datesPropType,
    handleSort: func,
    lastUpdate: datePropType,
    measurements: measurementsPropType,
    reports: reportsPropType,
    openReport: func,
    reload: func,
    reportDate: optionalDatePropType,
    reportsOverview: reportsOverviewPropType,
    settings: settingsPropType,
}
