import React from 'react';
import { Grid, Header, Icon, Menu, Tab } from 'semantic-ui-react';
import { StringInput } from '../fields/StringInput';
import { FocusableTab } from '../widgets/FocusableTab';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { ChangeLog } from '../changelog/ChangeLog';
import { DeleteButton, DownloadAsPDFButton } from '../widgets/Button';
import { delete_report, set_report_attribute, set_report_issue_tracker_attribute } from '../api/report';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { NotificationDestinations } from '../notification/NotificationDestinations';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { PasswordInput } from '../fields/PasswordInput';
import { Logo } from '../source/Logo';

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
        <>
            <DownloadAsPDFButton report_uuid={props.report_uuid} history={props.history} />
            <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
                <DeleteButton
                    item_type='report'
                    onClick={() => delete_report(props.report_uuid, props.go_home)}
                />}
            />
        </>
    )
}

const NONE_OPTION = {
    key: null, text: "None", value: null, content: 
        <Header as="h4">
            <Header.Content>None</Header.Content>
        </Header>
}

function IssueTracker({ datamodel, report_uuid, report, reload }) {

    let trackerSources = Object.entries(datamodel.sources).filter(
        ([source_name, source_type], index, array) => {
            return source_type["issue_tracker"] !== undefined
        }
    ).map(
        ([source_name, source_type], index, array) => {
            return {
                key: source_name,
                text: source_type.name,
                value: source_name,
                content:
                    <Header as="h4">
                        <Header.Content>
                            <Logo logo={source_name} alt={source_type.name} />{source_type.name}<Header.Subheader>{source_type.description}</Header.Subheader>
                        </Header.Content>
                    </Header>
            }
        }
    );
    trackerSources.push(NONE_OPTION)

    return (
        <Grid stackable>
            <Grid.Row columns={2}>
                <Grid.Column>
                    <SingleChoiceInput
                        id="tracker-type"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label="Issue tracker type"
                        options={trackerSources}
                        set_value={(value) => set_report_issue_tracker_attribute(report_uuid, "type", value, reload)}
                        value={report.issue_tracker?.type}
                    />
                </Grid.Column>
                <Grid.Column>
                    <StringInput
                        id="tracker-url"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label="Issue tracker URL"
                        set_value={(value) => set_report_issue_tracker_attribute(report_uuid, "url", value, reload)}
                        value={report.issue_tracker?.url}
                    />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row columns={2}>
                <Grid.Column>
                    <StringInput
                        id="tracker-username"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label="Username for basic authentication"
                        set_value={(value) => set_report_issue_tracker_attribute(report_uuid, "username", value, reload)}
                        value={report.issue_tracker?.username}
                    />
                </Grid.Column>
                <Grid.Column>
                    <PasswordInput
                        id="tracker-password"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label="Password for basic authentication"
                        set_value={(value) => set_report_issue_tracker_attribute(report_uuid, "password", value, reload)}
                        value={report.issue_tracker?.password}
                    />
                </Grid.Column>
            </Grid.Row>
        </Grid>
    )
}

export function ReportTitle({ datamodel, report, go_home, history, reload }) {
    const report_uuid = report.report_uuid;
    const panes = [
        { menuItem: <Menu.Item key="title"><Icon name="edit" /><FocusableTab>{"Title"}</FocusableTab></Menu.Item>, render: () => <Tab.Pane><ReportAttributes report_uuid={report_uuid} reload={reload} title={report.title} subtitle={report.subtitle} /></Tab.Pane> },
        { menuItem: <Menu.Item key="notifications"><Icon name="feed" /><FocusableTab>{"Notifications"}</FocusableTab></Menu.Item>, render: () => <Tab.Pane><NotificationDestinations destinations={report.notification_destinations || {}} report_uuid={report_uuid} reload={reload} /></Tab.Pane> },
        { menuItem: <Menu.Item key="issue_tracker"><Icon name="tasks" /><FocusableTab>{"Issue tracker"}</FocusableTab></Menu.Item>, render: () => <Tab.Pane><IssueTracker datamodel={datamodel} report_uuid={report_uuid} report={report} reload={reload} /></Tab.Pane>},
        { menuItem: <Menu.Item key="changelog"><Icon name="history" /><FocusableTab>{"Changelog"}</FocusableTab></Menu.Item>, render: () => <Tab.Pane><ChangeLog report_uuid={report_uuid} timestamp={report.timestamp} /></Tab.Pane> }
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
