import React, { useContext } from 'react';
import { Grid, Header, Icon, Menu } from 'semantic-ui-react';
import { Popup } from '../semantic_ui_react_wrappers/Popup';
import { Tab } from '../semantic_ui_react_wrappers/Tab';
import { Comment } from '../fields/Comment';
import { StringInput } from '../fields/StringInput';
import { FocusableTab } from '../widgets/FocusableTab';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
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

    const showIssueSummaryHelp = "Next to the issue status, also show the issue summary. Note: the popup over the issue always shows the issue summary, regardless of this setting."
    const showIssueSummaryLabel = <label>Show the issue summary <Popup on={['hover', 'focus']} content={showIssueSummaryHelp} trigger={<Icon tabIndex="0" name="help circle" />} /></label>
    const showIssueCreationDateHelp = "Next to the issue status, also show how long ago issue were created. Note: the popup over the issue always shows the exact date when the issue was created, regardless of this setting."
    const showIssueCreationDateLabel = <label>Show how long ago issues were created <Popup on={['hover', 'focus']} content={showIssueCreationDateHelp} trigger={<Icon tabIndex="0" name="help circle" />} /></label>
    const showIssueUpdateDateHelp = "Next to the issue status, also show how long ago issues were last updated. Note: the popup over the issue always shows the exact date when the issue was last updated, regardless of this setting."
    const showIssueUpdateDateLabel = <label>Show how long ago issues were updated <Popup on={['hover', 'focus']} content={showIssueUpdateDateHelp} trigger={<Icon tabIndex="0" name="help circle" />} /></label>

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
                        required={report.issue_tracker?.type && report.issue_tracker?.parameters?.username}
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label="Password for basic authentication"
                        set_value={(value) => set_report_issue_tracker_attribute(report_uuid, "password", value, reload)}
                        value={report.issue_tracker?.parameters?.password}
                    />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row columns={3}>
                <Grid.Column>
                    <SingleChoiceInput
                        id="issue-summary"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label={showIssueSummaryLabel}
                        options={[{ key: "yes", text: "Yes", value: true }, { key: "no", text: "No", value: false }]}
                        set_value={(value) => set_report_issue_tracker_attribute(report_uuid, "show_issue_summary", value, reload)}
                        value={report.issue_tracker?.parameters?.show_issue_summary ?? false}
                    />
                </Grid.Column>
                <Grid.Column>
                    <SingleChoiceInput
                        id="issue-creation-date"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label={showIssueCreationDateLabel}
                        options={[{ key: "yes", text: "Yes", value: true }, { key: "no", text: "No", value: false }]}
                        set_value={(value) => set_report_issue_tracker_attribute(report_uuid, "show_issue_creation_date", value, reload)}
                        value={report.issue_tracker?.parameters?.show_issue_creation_date ?? false}
                    />
                </Grid.Column>
                <Grid.Column>
                    <SingleChoiceInput
                        id="issue-update-date"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label={showIssueUpdateDateLabel}
                        options={[{ key: "yes", text: "Yes", value: true }, { key: "no", text: "No", value: false }]}
                        set_value={(value) => set_report_issue_tracker_attribute(report_uuid, "show_issue_update_date", value, reload)}
                        value={report.issue_tracker?.parameters?.show_issue_update_date ?? false}
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
