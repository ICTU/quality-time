import AssignmentIcon from "@mui/icons-material/Assignment"
import HistoryIcon from "@mui/icons-material/History"
import NotificationsIcon from "@mui/icons-material/Notifications"
import SellOutlinedIcon from "@mui/icons-material/SellOutlined"
import SettingsIcon from "@mui/icons-material/Settings"
import StorageIcon from "@mui/icons-material/Storage"
import TimerIcon from "@mui/icons-material/Timer"
import { func, string } from "prop-types"

import { deleteReport } from "../api/report"
import { ChangeLog } from "../changelog/ChangeLog"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import { NotificationDestinations } from "../notification/NotificationDestinations"
import { datesPropType, measurementsPropType, reportPropType, settingsPropType } from "../sharedPropTypes"
import { ButtonRow } from "../widgets/ButtonRow"
import { DeleteButton } from "../widgets/buttons/DeleteButton"
import { ExportReportButton } from "../widgets/buttons/ExportReportButton"
import { ExportReportCsvButton } from "../widgets/buttons/ExportReportCsvButton"
import { PermLinkButton } from "../widgets/buttons/PermLinkButton"
import { HeaderWithDetails } from "../widgets/HeaderWithDetails"
import { Tabs } from "../widgets/Tabs"
import { setDocumentTitle } from "./document_title"
import { IssueTracker } from "./IssueTracker"
import { ReactionTimes } from "./ReactionTimes"
import { ReportConfiguration } from "./ReportConfiguration"
import { ReportSources } from "./ReportSources"
import { Tags } from "./Tags"

function ReportTitleButtonRow({ report, measurements, dates, openReportsOverview, settings, url }) {
    const reportUuid = report.report_uuid
    const deleteButton = (
        <DeleteButton
            itemType="report"
            onClick={() => {
                deleteReport(reportUuid, openReportsOverview)
                settings.expandedItems.deleteItem(reportUuid)
            }}
        />
    )
    // The CSV export button is shown to all users because the CSV contains no credentials; the other buttons require
    // edit permission.
    return (
        <ButtonRow
            rightButton={
                <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={deleteButton} />
            }
            paddingBottom={2}
            paddingLeft={0}
            paddingRight={0}
            paddingTop={2}
        >
            <ExportReportCsvButton report={report} measurements={measurements} dates={dates} settings={settings} />
            <ReadOnlyOrEditable
                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                editableComponent={
                    <>
                        <ExportReportButton reportUuid={reportUuid} />
                        <PermLinkButton itemType="report" url={url} />
                    </>
                }
            />
        </ButtonRow>
    )
}
ReportTitleButtonRow.propTypes = {
    report: reportPropType,
    measurements: measurementsPropType,
    dates: datesPropType,
    openReportsOverview: func,
    settings: settingsPropType,
    url: string,
}

export function ReportTitle({ dates, measurements, openReportsOverview, reload, report, settings }) {
    const reportUuid = report.report_uuid
    const reportUrl = `${globalThis.location}`
    setDocumentTitle(report.title)
    return (
        <HeaderWithDetails
            header={report.title}
            itemUuid={reportUuid}
            level="h1"
            settings={settings}
            subheader={report.subtitle}
        >
            <Tabs
                settings={settings}
                tabs={[
                    { label: "Configuration", icon: <SettingsIcon /> },
                    { label: "Desired reaction times", icon: <TimerIcon /> },
                    { label: "Notifications", icon: <NotificationsIcon /> },
                    { label: "Issue tracker", icon: <AssignmentIcon /> },
                    { label: "Sources", icon: <StorageIcon /> },
                    { label: "Tags", icon: <SellOutlinedIcon /> },
                    { label: "Changelog", icon: <HistoryIcon /> },
                ]}
                uuid={reportUuid}
            >
                <ReportConfiguration report={report} reload={reload} />
                <ReactionTimes report={report} reload={reload} />
                <NotificationDestinations
                    destinations={report.notification_destinations || {}}
                    reportUuid={reportUuid}
                    reload={reload}
                />
                <IssueTracker report={report} reload={reload} />
                <ReportSources reload={reload} report={report} settings={settings} />
                <Tags reload={reload} report={report} />
                <ChangeLog reportUuid={reportUuid} timestamp={report.timestamp} />
            </Tabs>
            <ReportTitleButtonRow
                report={report}
                measurements={measurements}
                dates={dates}
                openReportsOverview={openReportsOverview}
                settings={settings}
                url={reportUrl}
            />
        </HeaderWithDetails>
    )
}
ReportTitle.propTypes = {
    dates: datesPropType,
    measurements: measurementsPropType,
    openReportsOverview: func,
    reload: func,
    report: reportPropType,
    settings: settingsPropType,
}
