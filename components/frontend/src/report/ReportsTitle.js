import React from 'react';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { Grid, Icon, Menu, Tab } from 'semantic-ui-react';
import { ChangeLog } from '../changelog/ChangeLog';
import { StringInput } from '../fields/StringInput';
import { MultipleChoiceInput } from '../fields/MultipleChoiceInput';
import { set_reports_attribute } from '../api/report';
import { EDIT_ENTITY_PERMISSION, EDIT_REPORT_PERMISSION } from '../context/Permissions';
import { FocusableTab } from '../widgets/FocusableTab';

function Title({ title, subtitle, reload }) {
    return (
        <Grid stackable>
            <Grid.Row columns={2}>
                <Grid.Column>
                    <StringInput
                        id="report_overview_title"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label="Report overview title"
                        set_value={(value) => set_reports_attribute("title", value, reload)}
                        value={title}
                    />
                </Grid.Column>
                <Grid.Column>
                    <StringInput
                        id="report_overview_subtitle"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label="Report overview subtitle"
                        set_value={(value) => set_reports_attribute("subtitle", value, reload)}
                        value={subtitle}
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

export function ReportsTitle({ permissions, title, subtitle, reload }) {
    const panes = [
        { menuItem: <Menu.Item key="title"><Icon name="edit" /><FocusableTab>{"Title"}</FocusableTab></Menu.Item>, render: () => <Tab.Pane><Title title={title} subtitle={subtitle} reload={reload} /></Tab.Pane> },
        { menuItem: <Menu.Item key="permissions"><Icon name="lock" /><FocusableTab>{"Permissions"}</FocusableTab></Menu.Item>, render: () => <Tab.Pane><Permissions permissions={permissions} reload={reload} /></Tab.Pane> },
        { menuItem: <Menu.Item key="changelog"><Icon name="history" /><FocusableTab>{"Changelog"}</FocusableTab></Menu.Item>, render: () => <Tab.Pane><ChangeLog /></Tab.Pane> }
    ]
    return (
        <HeaderWithDetails level="h1" header={title} subheader={subtitle}>
            <Tab panes={panes} />
        </HeaderWithDetails>
    )
}
