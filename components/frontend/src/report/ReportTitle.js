import { func, string } from "prop-types"
import { Grid } from "semantic-ui-react"

import { delete_report, set_report_attribute } from "../api/report"
import { activeTabIndex, tabChangeHandler } from "../app_ui_settings"
import { ChangeLog } from "../changelog/ChangeLog"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import { Comment } from "../fields/Comment"
import { IntegerInput } from "../fields/IntegerInput"
import { StringInput } from "../fields/StringInput"
import { STATUS_DESCRIPTION, STATUS_NAME } from "../metric/status"
import { NotificationDestinations } from "../notification/NotificationDestinations"
import { Label, Segment, Tab } from "../semantic_ui_react_wrappers"
import { reportPropType, settingsPropType } from "../sharedPropTypes"
import { getDesiredResponseTime } from "../utils"
import { DeleteButton, PermLinkButton } from "../widgets/Button"
import { HeaderWithDetails } from "../widgets/HeaderWithDetails"
import { LabelWithHelp } from "../widgets/LabelWithHelp"
import { changelogTabPane, configurationTabPane, tabPane } from "../widgets/TabPane"
import { setDocumentTitle } from "./document_title"
import { IssueTracker } from "./IssueTracker"

function ReportConfiguration({ reload, report }) {
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
ReportConfiguration.propTypes = {
    reload: func,
    report: reportPropType,
}

function ReactionTimes({ reload, report }) {
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
                                    set_report_attribute(
                                        report.report_uuid,
                                        "desired_response_times",
                                        desiredResponseTimes,
                                        reload,
                                    )
                                }}
                                unit="days"
                                value={getDesiredResponseTime(report, "unknown")}
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
                                    set_report_attribute(
                                        report.report_uuid,
                                        "desired_response_times",
                                        desiredResponseTimes,
                                        reload,
                                    )
                                }}
                                unit="days"
                                value={getDesiredResponseTime(report, "target_not_met")}
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
                                    set_report_attribute(
                                        report.report_uuid,
                                        "desired_response_times",
                                        desiredResponseTimes,
                                        reload,
                                    )
                                }}
                                unit="days"
                                value={getDesiredResponseTime(report, "near_target_met")}
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
                                    set_report_attribute(
                                        report.report_uuid,
                                        "desired_response_times",
                                        desiredResponseTimes,
                                        reload,
                                    )
                                }}
                                unit="days"
                                value={getDesiredResponseTime(report, "debt_target_met")}
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
                                    set_report_attribute(
                                        report.report_uuid,
                                        "desired_response_times",
                                        desiredResponseTimes,
                                        reload,
                                    )
                                }}
                                unit="days"
                                value={getDesiredResponseTime(report, "confirmed")}
                            />
                        </Grid.Column>
                        <Grid.Column>
                            <IntegerInput
                                id="desired-response-time-fixed"
                                label={
                                    <LabelWithHelp
                                        labelFor="desired-response-time-fixed"
                                        label="Fixed"
                                        help="Fixed means that an entity can be ignored because it has been fixed, or will be fixed shortly, and thus disappear."
                                    />
                                }
                                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                                set_value={(value) => {
                                    desiredResponseTimes["fixed"] = parseInt(value)
                                    set_report_attribute(
                                        report.report_uuid,
                                        "desired_response_times",
                                        desiredResponseTimes,
                                        reload,
                                    )
                                }}
                                unit="days"
                                value={getDesiredResponseTime(report, "fixed")}
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
                                    set_report_attribute(
                                        report.report_uuid,
                                        "desired_response_times",
                                        desiredResponseTimes,
                                        reload,
                                    )
                                }}
                                unit="days"
                                value={getDesiredResponseTime(report, "false_positive")}
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
                                    set_report_attribute(
                                        report.report_uuid,
                                        "desired_response_times",
                                        desiredResponseTimes,
                                        reload,
                                    )
                                }}
                                unit="days"
                                value={getDesiredResponseTime(report, "wont_fix")}
                            />
                        </Grid.Column>
                    </Grid.Row>
                </Grid>
            </Segment>
        </>
    )
}
ReactionTimes.propTypes = {
    reload: func,
    report: reportPropType,
}

function ButtonRow({ report_uuid, openReportsOverview, url }) {
    return (
        <ReadOnlyOrEditable
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            editableComponent={
                <span
                    /* The delete button needs to be in a span with an explicit height because otherwise it is
                       considered to have a height of zero. Maybe because it is floated right? Button rows that have
                       buttons on the left-hand side don't have this problem.
                    */
                    style={{ height: "36px", width: "100%", display: "block" }}
                >
                    <PermLinkButton itemType="report" url={url} />
                    <DeleteButton itemType="report" onClick={() => delete_report(report_uuid, openReportsOverview)} />
                </span>
            }
        />
    )
}
ButtonRow.propTypes = {
    report_uuid: string,
    openReportsOverview: func,
    url: string,
}

export function ReportTitle({ report, openReportsOverview, reload, settings }) {
    const report_uuid = report.report_uuid
    const tabIndex = activeTabIndex(settings.expandedItems, report_uuid)
    const reportUrl = `${window.location}`
    const panes = [
        configurationTabPane(<ReportConfiguration report={report} reload={reload} />),
        tabPane("Desired reaction times", <ReactionTimes report={report} reload={reload} />, { iconName: "time" }),
        tabPane(
            "Notifications",
            <NotificationDestinations
                destinations={report.notification_destinations || {}}
                report_uuid={report_uuid}
                reload={reload}
            />,
            { iconName: "feed" },
        ),
        tabPane("Issue tracker", <IssueTracker report={report} reload={reload} />, { iconName: "tasks" }),
        changelogTabPane(<ChangeLog report_uuid={report_uuid} timestamp={report.timestamp} />),
    ]
    setDocumentTitle(report.title)

    return (
        <HeaderWithDetails
            header={report.title}
            item_uuid={`${report.report_uuid}:${tabIndex}`}
            level="h1"
            settings={settings}
            subheader={report.subtitle}
        >
            <Tab
                defaultActiveIndex={tabIndex}
                onTabChange={tabChangeHandler(settings.expandedItems, report_uuid)}
                panes={panes}
            />
            <div style={{ marginTop: "20px" }}>
                <ButtonRow report_uuid={report_uuid} openReportsOverview={openReportsOverview} url={reportUrl} />
            </div>
        </HeaderWithDetails>
    )
}
ReportTitle.propTypes = {
    openReportsOverview: func,
    reload: func,
    report: reportPropType,
    settings: settingsPropType,
}
