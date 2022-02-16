import React from 'react';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { Grid, Icon, Menu, Tab } from 'semantic-ui-react';
import { ChangeLog } from '../changelog/ChangeLog';
import { Comment } from '../fields/Comment';
import { StringInput } from '../fields/StringInput';
import { MultipleChoiceInput } from '../fields/MultipleChoiceInput';
import { set_reports_attribute } from '../api/report';
import { EDIT_ENTITY_PERMISSION, EDIT_REPORT_PERMISSION } from '../context/Permissions';
import { FocusableTab } from '../widgets/FocusableTab';

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

function setPermissions(permissions, permission, value, reload) {
    permissions[permission] = value;
    set_reports_attribute("permissions", permissions, reload);
}

function Permissions({ permissions, reload }) {
    return (
        <Grid stackable>
            <Grid.Row columns={1}>
                <Grid.Column>
                    <MultipleChoiceInput
                        id="report_overview_edit_report_permission"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        allowAdditions
                        label="Users allowed to edit reports (user name or email address)"
                        options={permissions[EDIT_REPORT_PERMISSION] || []}
                        placeholder="All authenticated users"
                        set_value={(value) => setPermissions(permissions, EDIT_REPORT_PERMISSION, value, reload)}
                        value={permissions[EDIT_REPORT_PERMISSION]}
                    />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row columns={1}>
                <Grid.Column>
                    <MultipleChoiceInput
                        id="report_overview_edit_entity_permission"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        allowAdditions
                        label="Users allowed to edit measured entities (user name or email address)"
                        options={permissions[EDIT_ENTITY_PERMISSION] || []}
                        placeholder="All authenticated users"
                        set_value={(value) => setPermissions(permissions, EDIT_ENTITY_PERMISSION, value, reload)}
                        value={permissions[EDIT_ENTITY_PERMISSION]}
                    />
                </Grid.Column>
            </Grid.Row>
        </Grid>
    )
}

export function ReportsOverviewTitle({ reports_overview, reload }) {
    const panes = [
        { menuItem: <Menu.Item key="configuration"><Icon name="settings" /><FocusableTab>{"Configuration"}</FocusableTab></Menu.Item>, render: () => <Tab.Pane><ReportsOverviewConfiguration reports_overview={reports_overview} reload={reload} /></Tab.Pane> },
        { menuItem: <Menu.Item key="permissions"><Icon name="lock" /><FocusableTab>{"Permissions"}</FocusableTab></Menu.Item>, render: () => <Tab.Pane><Permissions permissions={reports_overview.permissions ?? {}} reload={reload} /></Tab.Pane> },
        { menuItem: <Menu.Item key="changelog"><Icon name="history" /><FocusableTab>{"Changelog"}</FocusableTab></Menu.Item>, render: () => <Tab.Pane><ChangeLog /></Tab.Pane> }
    ]
    return (
        <HeaderWithDetails level="h1" header={reports_overview.title} subheader={reports_overview.subtitle}>
            <Tab panes={panes} />
        </HeaderWithDetails>
    )
}
