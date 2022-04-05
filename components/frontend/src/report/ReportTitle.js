import React, { useContext } from 'react';
import { Grid, Header, Icon, Menu } from 'semantic-ui-react';
import { Popup, Tab } from '../semantic_ui_react_wrappers';
import { Comment } from '../fields/Comment';
import { StringInput } from '../fields/StringInput';
import { FocusableTab } from '../widgets/FocusableTab';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { HyperLink } from '../widgets/HyperLink';
import { ChangeLog } from '../changelog/ChangeLog';
import { Share } from '../share/Share';
import { DeleteButton, DownloadAsPDFButton } from '../widgets/Button';
import { delete_report, set_report_attribute, set_report_issue_tracker_attribute } from '../api/report';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { NotificationDestinations } from '../notification/NotificationDestinations';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { PasswordInput } from '../fields/PasswordInput';
import { Logo } from '../source/Logo';
import { DataModel } from '../context/DataModel';

function ReportConfiguration({ report, reload }) {
    return (
        <Grid stackable>
            <Grid.Row columns={2}>
                <Grid.Column>
                    <StringInput
                        id="report-title"
                        label="Report title"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        set_value={(value) => set_report_attribute(report.report_uuid, "title", value, reload)}
                        value={report.title}
                    />
                </Grid.Column>
                <Grid.Column>
                    <StringInput
                        id="report-subtitle"
                        label="Report subtitle"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        set_value={(value) => set_report_attribute(report.report_uuid, "subtitle", value, reload)}
                        value={report.subtitle}
                    />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row>
                <Grid.Column>
                    <Comment
                        id="report-comment"
                        set_value={(value) => set_report_attribute(report.report_uuid, "comment", value, reload)}
                        value={report.comment}
                    />
                </Grid.Column>
            </Grid.Row>
        </Grid>
    )
}

function ButtonRow({ report_uuid, go_home, history }) {
    return (
        <>
            <DownloadAsPDFButton report_uuid={report_uuid} history={history} />
            <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
                <DeleteButton
                    item_type='report'
                    onClick={() => delete_report(report_uuid, go_home)}
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

function IssueTracker({ report_uuid, report, reload }) {
    const dataModel = useContext(DataModel)
    let trackerSources = Object.entries(dataModel.sources).filter(
        ([source_name, source_type]) => { return source_type.issue_tracker === true }
    ).map(
        ([source_name, source_type]) => {
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
    var privateTokenLabel = "Private token";
    if (report.issue_tracker) {
        const help_url = dataModel.sources[report.issue_tracker?.type]?.parameters?.private_token?.help_url;
        if (help_url) {
            privateTokenLabel = <label>{privateTokenLabel} <HyperLink url={help_url}><Icon name="help circle" link /></HyperLink></label>
        }
    }

    return (
        <Grid stackable>
            <Grid.Row columns={2}>
                <Grid.Column>
                    <SingleChoiceInput
                        id="tracker-type"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        placeholder="None"
                        label="Issue tracker type"
                        options={trackerSources}
                        set_value={(value) => set_report_issue_tracker_attribute(report_uuid, "type", value, reload)}
                        value={report.issue_tracker?.type}
                    />
                </Grid.Column>
                <Grid.Column>
                    <StringInput
                        id="tracker-url"
                        required={report.issue_tracker?.type}
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label="Issue tracker URL"
                        set_value={(value) => set_report_issue_tracker_attribute(report_uuid, "url", value, reload)}
                        value={report.issue_tracker?.parameters?.url}
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
                        value={report.issue_tracker?.parameters?.username}
                    />
                </Grid.Column>
                <Grid.Column>
                    <PasswordInput
                        id="tracker-password"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label="Password for basic authentication"
                        set_value={(value) => set_report_issue_tracker_attribute(report_uuid, "password", value, reload)}
                        value={report.issue_tracker?.parameters?.password}
                    />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row columns={2}>
                <Grid.Column>
                    <PasswordInput
                        id="tracker-token"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label={privateTokenLabel}
                        set_value={(value) => set_report_issue_tracker_attribute(report_uuid, "private_token", value, reload)}
                        value={report.issue_tracker?.parameters?.private_token}
                    />
                </Grid.Column>
            </Grid.Row>
        </Grid>
    )
}

export function ReportTitle({ report, go_home, history, reload }) {
    const report_uuid = report.report_uuid;
    const reportUrl = `${window.location}`;
    const panes = [
        {
            menuItem: <Menu.Item key="configuration"><Icon name="settings" /><FocusableTab>{"Configuration"}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane><ReportConfiguration report={report} reload={reload} /></Tab.Pane>
        },
        {
            menuItem: <Menu.Item key="notifications"><Icon name="feed" /><FocusableTab>{"Notifications"}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane><NotificationDestinations destinations={report.notification_destinations || {}} report_uuid={report_uuid} reload={reload} /></Tab.Pane>
        },
        {
            menuItem: <Menu.Item key="issue_tracker"><Icon name="tasks" /><FocusableTab>{"Issue tracker"}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane><IssueTracker report_uuid={report_uuid} report={report} reload={reload} /></Tab.Pane>
        },
        {
            menuItem: <Menu.Item key="changelog"><Icon name="history" /><FocusableTab>{"Changelog"}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane><ChangeLog report_uuid={report_uuid} timestamp={report.timestamp} /></Tab.Pane>
        },
        {
            menuItem: <Menu.Item key="share"><Icon name="share square" /><FocusableTab>{'Share'}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane><Share title="Report permanent link" url={reportUrl} /></Tab.Pane>
        }
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
