import React from 'react';
import { Grid, Icon, Menu } from 'semantic-ui-react';
import { Label, Segment, Tab } from '../semantic_ui_react_wrappers';
import { Comment } from '../fields/Comment';
import { IntegerInput } from '../fields/IntegerInput';
import { StringInput } from '../fields/StringInput';
import { FocusableTab } from '../widgets/FocusableTab';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { LabelWithHelp } from '../widgets/LabelWithHelp';
import { ChangeLog } from '../changelog/ChangeLog';
import { Share } from '../share/Share';
import { DeleteButton, DownloadAsPDFButton } from '../widgets/Button';
import { delete_report, set_report_attribute } from '../api/report';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { NotificationDestinations } from '../notification/NotificationDestinations';
import { IssueTracker } from './IssueTracker';
import { defaultDesiredResponseTimes } from '../defaults';
import { setDocumentTitle } from './document_title';
import { STATUS_DESCRIPTION, STATUS_NAME } from '../utils';

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

function ReactionTimes({ report, reload }) {
    const desiredResponseTimes = report.desired_response_times ?? {}
    return (
        <>
            <Segment>
                <Label attached="top" size="large">
                    Desired metric response times
                </Label>
                <Grid stackable>
                    <Grid.Row columns={4}>
                        <Grid.Column>
                            <IntegerInput
                                id="desired-response-time-white"
                                label={
                                    <LabelWithHelp
                                        labelFor="desired-response-time-white"
                                        label={STATUS_NAME.unknown}
                                        help={STATUS_DESCRIPTION.unknown}
                                    />
                                }
                                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                                set_value={(value) => {
                                    desiredResponseTimes["unknown"] = parseInt(value)
                                    set_report_attribute(report.report_uuid, "desired_response_times", desiredResponseTimes, reload)
                                }}
                                unit="days"
                                value={desiredResponseTimes["unknown"] ?? defaultDesiredResponseTimes["unknown"]}
                            />
                        </Grid.Column>
                        <Grid.Column>
                            <IntegerInput
                                id="desired-response-time-red"
                                label={
                                    <LabelWithHelp
                                        labelFor="desired-response-time-red"
                                        label={STATUS_NAME.target_not_met}
                                        help={STATUS_DESCRIPTION.target_not_met}
                                    />
                                }
                                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                                set_value={(value) => {
                                    desiredResponseTimes["target_not_met"] = parseInt(value)
                                    set_report_attribute(report.report_uuid, "desired_response_times", desiredResponseTimes, reload)
                                }}
                                unit="days"
                                value={desiredResponseTimes["target_not_met"] ?? defaultDesiredResponseTimes["target_not_met"]}
                            />
                        </Grid.Column>
                        <Grid.Column>
                            <IntegerInput
                                id="desired-response-time-yellow"
                                label={
                                    <LabelWithHelp
                                        labelFor="desired-response-time-yellow"
                                        label={STATUS_NAME.near_target_met}
                                        help={STATUS_DESCRIPTION.near_target_met}
                                    />
                                }
                                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                                set_value={(value) => {
                                    desiredResponseTimes["near_target_met"] = parseInt(value)
                                    set_report_attribute(report.report_uuid, "desired_response_times", desiredResponseTimes, reload)
                                }}
                                unit="days"
                                value={desiredResponseTimes["near_target_met"] ?? defaultDesiredResponseTimes["near_target_met"]}
                            />
                        </Grid.Column>
                        <Grid.Column>
                            <IntegerInput
                                id="desired-response-time-grey"
                                label={
                                    <LabelWithHelp
                                        hoverable
                                        labelFor="desired-response-time-grey"
                                        label={STATUS_NAME.debt_target_met}
                                        help={STATUS_DESCRIPTION.debt_target_met}
                                    />
                                }
                                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                                set_value={(value) => {
                                    desiredResponseTimes["debt_target_met"] = parseInt(value)
                                    set_report_attribute(report.report_uuid, "desired_response_times", desiredResponseTimes, reload)
                                }}
                                unit="days"
                                value={desiredResponseTimes["debt_target_met"] ?? defaultDesiredResponseTimes["debt_target_met"]}
                            />
                        </Grid.Column>
                    </Grid.Row>
                </Grid>
            </Segment>
            <Segment>
                <Label attached="top" size="large">
                    Desired time after which to review measurement entities (violations, warnings, issues, etc.)
                </Label>
                <Grid stackable>
                    <Grid.Row columns={4}>
                        <Grid.Column>
                            <IntegerInput
                                id="desired-response-time-confirmed"
                                label={
                                    <LabelWithHelp
                                        labelFor="desired-response-time-confirmed"
                                        label="Confirmed"
                                        help="Confirmed means that an entity has been reviewed and should be dealt with."
                                    />
                                }
                                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                                set_value={(value) => {
                                    desiredResponseTimes["confirmed"] = parseInt(value)
                                    set_report_attribute(report.report_uuid, "desired_response_times", desiredResponseTimes, reload)
                                }}
                                unit="days"
                                value={desiredResponseTimes["confirmed"] ?? defaultDesiredResponseTimes["confirmed"]}
                            />
                        </Grid.Column>
                        <Grid.Column>
                            <IntegerInput
                                id="desired-response-time-fixed"
                                label={
                                    <LabelWithHelp
                                        labelFor="desired-response-time-fixed"
                                        label="Will be fixed"
                                        help="Will be fixed means that an entity can be ignored because it will be fixed shortly and thus disappear."
                                    />
                                }
                                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                                set_value={(value) => {
                                    desiredResponseTimes["fixed"] = parseInt(value)
                                    set_report_attribute(report.report_uuid, "desired_response_times", desiredResponseTimes, reload)
                                }}
                                unit="days"
                                value={desiredResponseTimes["fixed"] ?? defaultDesiredResponseTimes["fixed"]}
                            />
                        </Grid.Column>
                        <Grid.Column>
                            <IntegerInput
                                id="desired-response-time-false-positive"
                                label={
                                    <LabelWithHelp
                                        labelFor="desired-response-time-false-positive"
                                        label="False positive"
                                        help="False positive means an entity has been incorrectly identified as a problem and should be ignored."
                                    />
                                }
                                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                                set_value={(value) => {
                                    desiredResponseTimes["false_positive"] = parseInt(value)
                                    set_report_attribute(report.report_uuid, "desired_response_times", desiredResponseTimes, reload)
                                }}
                                unit="days"
                                value={desiredResponseTimes["false_positive"] ?? defaultDesiredResponseTimes["false_positive"]}
                            />
                        </Grid.Column>
                        <Grid.Column>
                            <IntegerInput
                                id="desired-response-time-wont-fix"
                                label={
                                    <LabelWithHelp
                                        labelFor="desired-response-time-wont-fix"
                                        label="Won't fix"
                                        help="Won't fix means that an entity can be ignored because it will not be fixed."
                                    />
                                }
                                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                                set_value={(value) => {
                                    desiredResponseTimes["wont_fix"] = parseInt(value)
                                    set_report_attribute(report.report_uuid, "desired_response_times", desiredResponseTimes, reload)
                                }}
                                unit="days"
                                value={desiredResponseTimes["wont_fix"] ?? defaultDesiredResponseTimes["wont_fix"]}
                            />
                        </Grid.Column>
                    </Grid.Row>
                </Grid>
            </Segment>
        </>
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

export function ReportTitle({ report, go_home, history, reload }) {
    const report_uuid = report.report_uuid;
    const reportUrl = `${window.location}`;
    const panes = [
        {
            menuItem: <Menu.Item key="configuration"><Icon name="settings" /><FocusableTab>{"Configuration"}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane><ReportConfiguration report={report} reload={reload} /></Tab.Pane>
        },
        {
            menuItem: <Menu.Item key="reaction_times"><Icon name="time" /><FocusableTab>{"Desired reaction times"}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane><ReactionTimes report={report} reload={reload} /></Tab.Pane>
        },
        {
            menuItem: <Menu.Item key="notifications"><Icon name="feed" /><FocusableTab>{"Notifications"}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane><NotificationDestinations destinations={report.notification_destinations || {}} report_uuid={report_uuid} reload={reload} /></Tab.Pane>
        },
        {
            menuItem: <Menu.Item key="issue_tracker"><Icon name="tasks" /><FocusableTab>{"Issue tracker"}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane><IssueTracker report={report} reload={reload} /></Tab.Pane>
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
    setDocumentTitle(report.title);
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
