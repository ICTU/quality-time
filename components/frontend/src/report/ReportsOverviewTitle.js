import Grid from "@mui/material/Grid2"
import { func, shape } from "prop-types"

import { set_reports_attribute } from "../api/report"
import { activeTabIndex, tabChangeHandler } from "../app_ui_settings"
import { ChangeLog } from "../changelog/ChangeLog"
import { EDIT_ENTITY_PERMISSION, EDIT_REPORT_PERMISSION } from "../context/Permissions"
import { Comment } from "../fields/Comment"
import { MultipleChoiceInput } from "../fields/MultipleChoiceInput"
import { StringInput } from "../fields/StringInput"
import { Tab } from "../semantic_ui_react_wrappers"
import { permissionsPropType, reportsOverviewPropType, settingsPropType } from "../sharedPropTypes"
import { dropdownOptions } from "../utils"
import { HeaderWithDetails } from "../widgets/HeaderWithDetails"
import { changelogTabPane, configurationTabPane, tabPane } from "../widgets/TabPane"
import { setDocumentTitle } from "./document_title"

function ReportsOverviewConfiguration({ reports_overview, reload }) {
    return (
        <Grid container alignItems="flex-end" spacing={{ xs: 1, sm: 1, md: 2 }} columns={{ xs: 1, sm: 2, md: 2 }}>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <StringInput
                    id="reports-overview-title"
                    requiredPermissions={[EDIT_REPORT_PERMISSION]}
                    label="Report overview title"
                    set_value={(value) => set_reports_attribute("title", value, reload)}
                    value={reports_overview.title}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <StringInput
                    id="reports-overview-subtitle"
                    requiredPermissions={[EDIT_REPORT_PERMISSION]}
                    label="Report overview subtitle"
                    set_value={(value) => set_reports_attribute("subtitle", value, reload)}
                    value={reports_overview.subtitle}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 2, md: 2 }}>
                <Comment
                    id="reports-overview-comment"
                    set_value={(value) => set_reports_attribute("comment", value, reload)}
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

function Permissions({ permissions, reload }) {
    return (
        <Grid container alignItems="flex-end" spacing={{ xs: 1, sm: 1, md: 2 }} columns={{ xs: 1, sm: 1, md: 2 }}>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <MultipleChoiceInput
                    allowAdditions
                    id="report_overview_edit_report_permission"
                    label="Users allowed to edit reports (user name or email address)"
                    options={dropdownOptions(permissions[EDIT_REPORT_PERMISSION] || [])}
                    placeholder="All authenticated users"
                    requiredPermissions={[EDIT_REPORT_PERMISSION]}
                    set_value={(value) => setPermissions(permissions, EDIT_REPORT_PERMISSION, value, reload)}
                    value={permissions[EDIT_REPORT_PERMISSION]}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <MultipleChoiceInput
                    allowAdditions
                    id="report_overview_edit_entity_permission"
                    label="Users allowed to edit measured entities (user name or email address)"
                    options={dropdownOptions(permissions[EDIT_ENTITY_PERMISSION] || [])}
                    placeholder="All authenticated users"
                    requiredPermissions={[EDIT_REPORT_PERMISSION]}
                    set_value={(value) => setPermissions(permissions, EDIT_ENTITY_PERMISSION, value, reload)}
                    value={permissions[EDIT_ENTITY_PERMISSION]}
                />
            </Grid>
        </Grid>
    )
}
Permissions.propTypes = {
    permissions: shape({
        EDIT_REPORT_PERMISSION: permissionsPropType,
        EDIT_ENTITY_PERMISSION: permissionsPropType,
    }),
    reload: func,
}

export function ReportsOverviewTitle({ reports_overview, reload, settings }) {
    const uuid = "reports_overview"
    const tabIndex = activeTabIndex(settings.expandedItems, uuid)
    const panes = [
        configurationTabPane(<ReportsOverviewConfiguration reports_overview={reports_overview} reload={reload} />),
        tabPane("Permissions", <Permissions permissions={reports_overview.permissions ?? {}} reload={reload} />, {
            iconName: "lock",
        }),
        changelogTabPane(<ChangeLog />),
    ]
    setDocumentTitle(reports_overview.title)

    return (
        <HeaderWithDetails
            header={reports_overview.title}
            item_uuid={`${uuid}:${tabIndex}`}
            level="h1"
            settings={settings}
            subheader={reports_overview.subtitle}
        >
            <Tab
                defaultActiveIndex={tabIndex}
                onTabChange={tabChangeHandler(settings.expandedItems, uuid)}
                panes={panes}
            />
        </HeaderWithDetails>
    )
}
ReportsOverviewTitle.propTypes = {
    reports_overview: reportsOverviewPropType,
    reload: func,
    settings: settingsPropType,
}
