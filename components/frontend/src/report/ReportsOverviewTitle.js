import HistoryIcon from "@mui/icons-material/History"
import LockIcon from "@mui/icons-material/Lock"
import SettingsIcon from "@mui/icons-material/Settings"
import Grid from "@mui/material/Grid2"
import { func, shape } from "prop-types"
import { useContext } from "react"

import { set_reports_attribute } from "../api/report"
import { ChangeLog } from "../changelog/ChangeLog"
import { accessGranted, EDIT_ENTITY_PERMISSION, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { CommentField } from "../fields/CommentField"
import { MultipleChoiceField } from "../fields/MultipleChoiceField"
import { TextField } from "../fields/TextField"
import { permissionsPropType, reportsOverviewPropType, settingsPropType } from "../sharedPropTypes"
import { HeaderWithDetails } from "../widgets/HeaderWithDetails"
import { Tabs } from "../widgets/Tabs"
import { setDocumentTitle } from "./document_title"

function ReportsOverviewConfiguration({ reports_overview, reload }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    return (
        <Grid container alignItems="flex-end" spacing={{ xs: 1, sm: 1, md: 2 }} columns={{ xs: 1, sm: 2, md: 2 }}>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={disabled}
                    id="reports-overview-title"
                    label="Report overview title"
                    onChange={(value) => set_reports_attribute("title", value, reload)}
                    value={reports_overview.title}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={disabled}
                    id="reports-overview-subtitle"
                    label="Report overview subtitle"
                    onChange={(value) => set_reports_attribute("subtitle", value, reload)}
                    value={reports_overview.subtitle}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 2, md: 2 }}>
                <CommentField
                    disabled={disabled}
                    id="reports-overview-comment"
                    onChange={(value) => set_reports_attribute("comment", value, reload)}
                    value={reports_overview.comment}
                />
            </Grid>
        </Grid>
    )
}
ReportsOverviewConfiguration.propTypes = {
    reports_overview: reportsOverviewPropType,
    reload: func,
}

function setPermissions(permissions, permission, value, reload) {
    permissions[permission] = value
    set_reports_attribute("permissions", permissions, reload)
}

function PermissionsConfiguration({ permissions, reload }) {
    const currentPermissions = useContext(Permissions)
    const disabled = !accessGranted(currentPermissions, [EDIT_REPORT_PERMISSION])
    return (
        <Grid container alignItems="flex-end" spacing={{ xs: 1, sm: 1, md: 2 }} columns={{ xs: 1, sm: 1, md: 2 }}>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <MultipleChoiceField
                    disabled={disabled}
                    freeSolo
                    id="report_overview_edit_report_permission"
                    label="Users allowed to edit reports (user name or email address)"
                    onChange={(value) => setPermissions(permissions, EDIT_REPORT_PERMISSION, value, reload)}
                    options={permissions[EDIT_REPORT_PERMISSION] || []}
                    placeholder="All authenticated users"
                    value={permissions[EDIT_REPORT_PERMISSION] || []}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <MultipleChoiceField
                    disabled={disabled}
                    freeSolo
                    id="report_overview_edit_entity_permission"
                    label="Users allowed to edit measured entities (user name or email address)"
                    onChange={(value) => setPermissions(permissions, EDIT_ENTITY_PERMISSION, value, reload)}
                    options={permissions[EDIT_ENTITY_PERMISSION] || []}
                    placeholder="All authenticated users"
                    value={permissions[EDIT_ENTITY_PERMISSION] || []}
                />
            </Grid>
        </Grid>
    )
}
PermissionsConfiguration.propTypes = {
    permissions: shape({
        EDIT_REPORT_PERMISSION: permissionsPropType,
        EDIT_ENTITY_PERMISSION: permissionsPropType,
    }),
    reload: func,
}

export function ReportsOverviewTitle({ reports_overview, reload, settings }) {
    const uuid = "reports_overview"
    setDocumentTitle(reports_overview.title)

    return (
        <HeaderWithDetails
            header={reports_overview.title}
            item_uuid={uuid}
            level="h1"
            settings={settings}
            subheader={reports_overview.subtitle}
        >
            <Tabs
                tabs={[
                    { label: "Configuration", icon: <SettingsIcon /> },
                    { label: "Permissions", icon: <LockIcon /> },
                    { label: "Changelog", icon: <HistoryIcon /> },
                ]}
            >
                <ReportsOverviewConfiguration reports_overview={reports_overview} reload={reload} />
                <PermissionsConfiguration permissions={reports_overview.permissions ?? {}} reload={reload} />
                <ChangeLog />
            </Tabs>
        </HeaderWithDetails>
    )
}
ReportsOverviewTitle.propTypes = {
    reports_overview: reportsOverviewPropType,
    reload: func,
    settings: settingsPropType,
}
