import React from 'react';
import { Menu, Grid, Tab } from 'semantic-ui-react';
import { StringInput } from '../fields/StringInput';
import { FocusableTab } from '../widgets/FocusableTab';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { ChangeLog } from '../changelog/ChangeLog';
import { DeleteButton, DownloadAsPDFButton } from '../widgets/Button';
import { delete_report, set_report_attribute } from '../api/report';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { NotificationDestinations } from '../notification/NotificationDestinations';

function ReportAttributes(props) {
    return (
        <Grid stackable>
            <Grid.Row columns={2}>
                <Grid.Column>
                    <StringInput
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        id="report-title"
                        label="Report title"
                        set_value={(value) => set_report_attribute(props.report_uuid, "title", value, props.reload)}
                        value={props.title}
                    />
                </Grid.Column>
                <Grid.Column>
                    <StringInput
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        id="report-subtitle"
                        label="Report subtitle"
                        set_value={(value) => set_report_attribute(props.report_uuid, "subtitle", value, props.reload)}
                        value={props.subtitle}
                    />
                </Grid.Column>
            </Grid.Row>
        </Grid>
    )
}

function ButtonRow(props) {
    return (
        <Grid.Row>
            <Grid.Column>
                <DownloadAsPDFButton report_uuid={props.report_uuid} history={props.history} />
                <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
                    <DeleteButton
                        item_type='report'
                        onClick={() => delete_report(props.report_uuid, props.go_home)}
                    />}
                />
            </Grid.Column>
        </Grid.Row>
    )
}

export function ReportTitle({ report, go_home, history, reload }) {
    const report_uuid = report.report_uuid;
    const panes = [
        { menuItem: <Menu.Item key="title"><FocusableTab>{"Title"}</FocusableTab></Menu.Item>, render: () => <Tab.Pane><ReportAttributes report_uuid={report_uuid} reload={reload} title={report.title} subtitle={report.subtitle} /></Tab.Pane> },
        { menuItem: <Menu.Item key="notifications"><FocusableTab>{"Notifications"}</FocusableTab></Menu.Item>, render: () => <Tab.Pane><NotificationDestinations destinations={report.notification_destinations || {}} report_uuid={report_uuid} reload={reload} /></Tab.Pane> },
        { menuItem: <Menu.Item key="changelog"><FocusableTab>{"Changelog"}</FocusableTab></Menu.Item>, render: () => <Tab.Pane><ChangeLog report_uuid={report_uuid} timestamp={report.timestamp} /></Tab.Pane> }
    ]
    return (
        <HeaderWithDetails level="h1" header={report.title} subheader={report.subtitle}>
            <>
                <Tab panes={panes} />
                <div style={{ marginTop: "20px" }}>
                    <ButtonRow report_uuid={report_uuid} go_home={go_home} history={history} />
                </div>
            </>
        </HeaderWithDetails>
    )
}
