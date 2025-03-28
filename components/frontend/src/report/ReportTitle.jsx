import AssignmentIcon from "@mui/icons-material/Assignment"
import HistoryIcon from "@mui/icons-material/History"
import NotificationsIcon from "@mui/icons-material/Notifications"
import SettingsIcon from "@mui/icons-material/Settings"
import TimerIcon from "@mui/icons-material/Timer"
import { Typography } from "@mui/material"
import Grid from "@mui/material/Grid"
import { func, oneOfType, string } from "prop-types"
import { useContext } from "react"

import { delete_report, set_report_attribute } from "../api/report"
import { ChangeLog } from "../changelog/ChangeLog"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions, ReadOnlyOrEditable } from "../context/Permissions"
import { CommentField } from "../fields/CommentField"
import { TextField } from "../fields/TextField"
import { STATUS_DESCRIPTION, STATUS_NAME, statusPropType } from "../metric/status"
import { NotificationDestinations } from "../notification/NotificationDestinations"
import { entityStatusPropType, reportPropType, settingsPropType } from "../sharedPropTypes"
import { SOURCE_ENTITY_STATUS_DESCRIPTION, SOURCE_ENTITY_STATUS_NAME } from "../source/source_entity_status"
import { getDesiredResponseTime } from "../utils"
import { ButtonRow } from "../widgets/ButtonRow"
import { DeleteButton } from "../widgets/buttons/DeleteButton"
import { PermLinkButton } from "../widgets/buttons/PermLinkButton"
import { HeaderWithDetails } from "../widgets/HeaderWithDetails"
import { Tabs } from "../widgets/Tabs"
import { setDocumentTitle } from "./document_title"
import { IssueTracker } from "./IssueTracker"

function ReportConfiguration({ reload, report }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    return (
        <Grid container alignItems="flex-end" spacing={{ xs: 1, sm: 1, md: 2 }} columns={{ xs: 1, sm: 2, md: 2 }}>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={disabled}
                    id="report_title"
                    label="Report title"
                    onChange={(value) => set_report_attribute(report.report_uuid, "title", value, reload)}
                    value={report.title}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={disabled}
                    id="report-subtitle"
                    label="Report subtitle"
                    onChange={(value) => set_report_attribute(report.report_uuid, "subtitle", value, reload)}
                    value={report.subtitle}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 2, md: 2 }}>
                <CommentField
                    disabled={disabled}
                    id="report-comment"
                    onChange={(value) => set_report_attribute(report.report_uuid, "comment", value, reload)}
                    value={report.comment}
                />
            </Grid>
        </Grid>
    )
}
ReportConfiguration.propTypes = {
    reload: func,
    report: reportPropType,
}

function DesiredResponseTimeInput({ reload, report, status }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const desiredResponseTimes = report.desired_response_times ?? {}
    const inputId = `desired-response-time-${status}`
    const label = STATUS_NAME[status] || SOURCE_ENTITY_STATUS_NAME[status]
    const help = STATUS_DESCRIPTION[status] || SOURCE_ENTITY_STATUS_DESCRIPTION[status]
    return (
        <TextField
            disabled={disabled}
            endAdornment="days"
            helperText={help}
            id={inputId}
            label={label}
            onChange={(value) => {
                desiredResponseTimes[status] = parseInt(value)
                set_report_attribute(report.report_uuid, "desired_response_times", desiredResponseTimes, reload)
            }}
            type="number"
            value={getDesiredResponseTime(report, status)?.toString()}
        />
    )
}
DesiredResponseTimeInput.propTypes = {
    reload: func,
    report: reportPropType,
    status: oneOfType([statusPropType, entityStatusPropType]),
}

function ReactionTimes(props) {
    return (
        <Grid container alignItems="flex-start" spacing={{ xs: 1, sm: 2, md: 2 }} columns={{ xs: 1, sm: 2, md: 4 }}>
            <Grid size={{ xs: 1, sm: 2, md: 4 }}>
                <Typography>Desired metric response times</Typography>
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <DesiredResponseTimeInput status="unknown" {...props} />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <DesiredResponseTimeInput status="target_not_met" {...props} />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <DesiredResponseTimeInput status="near_target_met" {...props} />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <DesiredResponseTimeInput hoverableLabel status="debt_target_met" {...props} />
            </Grid>
            <Grid size={{ xs: 1, sm: 2, md: 4 }}>
                <Typography>
                    Desired time after which to review measurement entities (violations, warnings, issues, etc.)
                </Typography>
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <DesiredResponseTimeInput status="confirmed" {...props} />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <DesiredResponseTimeInput status="fixed" {...props} />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <DesiredResponseTimeInput status="false_positive" {...props} />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <DesiredResponseTimeInput status="wont_fix" {...props} />
            </Grid>
        </Grid>
    )
}
ReactionTimes.propTypes = {
    reload: func,
    report: reportPropType,
}

function ReportTitleButtonRow({ report_uuid, openReportsOverview, settings, url }) {
    const deleteButton = (
        <DeleteButton
            itemType="report"
            onClick={() => {
                delete_report(report_uuid, openReportsOverview)
                settings.expandedItems.deleteItem(report_uuid)
            }}
        />
    )
    return (
        <ReadOnlyOrEditable
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            editableComponent={
                <ButtonRow rightButton={deleteButton} paddingBottom={2} paddingLeft={0} paddingRight={0} paddingTop={2}>
                    <PermLinkButton itemType="report" url={url} />
                </ButtonRow>
            }
        />
    )
}
ReportTitleButtonRow.propTypes = {
    report_uuid: string,
    openReportsOverview: func,
    settings: settingsPropType,
    url: string,
}

export function ReportTitle({ report, openReportsOverview, reload, settings }) {
    const report_uuid = report.report_uuid
    const reportUrl = `${window.location}`
    setDocumentTitle(report.title)
    return (
        <HeaderWithDetails
            header={report.title}
            item_uuid={report.report_uuid}
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
                    { label: "Changelog", icon: <HistoryIcon /> },
                ]}
                uuid={report_uuid}
            >
                <ReportConfiguration report={report} reload={reload} />
                <ReactionTimes report={report} reload={reload} />
                <NotificationDestinations
                    destinations={report.notification_destinations || {}}
                    report_uuid={report_uuid}
                    reload={reload}
                />
                <IssueTracker report={report} reload={reload} />
                <ChangeLog report_uuid={report_uuid} timestamp={report.timestamp} />
            </Tabs>
            <ReportTitleButtonRow
                report_uuid={report_uuid}
                openReportsOverview={openReportsOverview}
                settings={settings}
                url={reportUrl}
            />
        </HeaderWithDetails>
    )
}
ReportTitle.propTypes = {
    openReportsOverview: func,
    reload: func,
    report: reportPropType,
    settings: settingsPropType,
}
