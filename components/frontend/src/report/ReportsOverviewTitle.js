import { func, shape } from "prop-types"
import { Grid, Icon, Menu } from "semantic-ui-react"

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
import { FocusableTab } from "../widgets/FocusableTab"
import { HeaderWithDetails } from "../widgets/HeaderWithDetails"
import { setDocumentTitle } from "./document_title"

function ReportsOverviewConfiguration({ reports_overview, reload }) {
    return (
        <Grid stackable>
            <Grid.Row columns={2}>
                <Grid.Column>
                    <StringInput
                        id="reports-overview-title"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label="Report overview title"
                        set_value={(value) => set_reports_attribute("title", value, reload)}
                        value={reports_overview.title}
                    />
                </Grid.Column>
                <Grid.Column>
                    <StringInput
                        id="reports-overview-subtitle"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label="Report overview subtitle"
                        set_value={(value) => set_reports_attribute("subtitle", value, reload)}
                        value={reports_overview.subtitle}
                    />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row>
                <Grid.Column>
                    <Comment
                        id="reports-overview-comment"
                        set_value={(value) => set_reports_attribute("comment", value, reload)}
                        value={reports_overview.comment}
                    />
                </Grid.Column>
            </Grid.Row>
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
        <Grid stackable>
            <Grid.Row columns={1}>
                <Grid.Column>
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
                </Grid.Column>
            </Grid.Row>
            <Grid.Row columns={1}>
                <Grid.Column>
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
                </Grid.Column>
            </Grid.Row>
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
        {
            menuItem: (
                <Menu.Item key="configuration">
                    <Icon name="settings" />
                    <FocusableTab>{"Configuration"}</FocusableTab>
                </Menu.Item>
            ),
            render: () => (
                <Tab.Pane>
                    <ReportsOverviewConfiguration reports_overview={reports_overview} reload={reload} />
                </Tab.Pane>
            ),
        },
        {
            menuItem: (
                <Menu.Item key="permissions">
                    <Icon name="lock" />
                    <FocusableTab>{"Permissions"}</FocusableTab>
                </Menu.Item>
            ),
            render: () => (
                <Tab.Pane>
                    <Permissions permissions={reports_overview.permissions ?? {}} reload={reload} />
                </Tab.Pane>
            ),
        },
        {
            menuItem: (
                <Menu.Item key="changelog">
                    <Icon name="history" />
                    <FocusableTab>{"Changelog"}</FocusableTab>
                </Menu.Item>
            ),
            render: () => (
                <Tab.Pane>
                    <ChangeLog />
                </Tab.Pane>
            ),
        },
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
