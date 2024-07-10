import { bool, func, oneOfType, string } from "prop-types"
import { Grid } from "semantic-ui-react"

import { delete_report, set_report_attribute } from "../api/report"
import { activeTabIndex, tabChangeHandler } from "../app_ui_settings"
import { ChangeLog } from "../changelog/ChangeLog"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import { Comment } from "../fields/Comment"
import { IntegerInput } from "../fields/IntegerInput"
import { StringInput } from "../fields/StringInput"
import { STATUS_DESCRIPTION, STATUS_NAME, statusPropType } from "../metric/status"
import { NotificationDestinations } from "../notification/NotificationDestinations"
import { Label, Segment, Tab } from "../semantic_ui_react_wrappers"
import { entityStatusPropType, reportPropType, settingsPropType } from "../sharedPropTypes"
import { SOURCE_ENTITY_STATUS_DESCRIPTION, SOURCE_ENTITY_STATUS_NAME } from "../source/source_entity_status"
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

function DesiredResponseTimeInput({ hoverableLabel, reload, report, status }) {
    const desiredResponseTimes = report.desired_response_times ?? {}
    const inputId = `desired-response-time-${status}`
    const label = STATUS_NAME[status] || SOURCE_ENTITY_STATUS_NAME[status]
    const help = STATUS_DESCRIPTION[status] || SOURCE_ENTITY_STATUS_DESCRIPTION[status]
    return (
        <IntegerInput
            allowEmpty
            id={inputId}
            label={<LabelWithHelp hoverable={hoverableLabel} labelFor={inputId} label={label} help={help} />}
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            set_value={(value) => {
                desiredResponseTimes[status] = parseInt(value)
                set_report_attribute(report.report_uuid, "desired_response_times", desiredResponseTimes, reload)
            }}
            unit="days"
            value={getDesiredResponseTime(report, status)}
        />
    )
}
DesiredResponseTimeInput.propTypes = {
    hoverableLabel: bool,
    reload: func,
    report: reportPropType,
    status: oneOfType([statusPropType, entityStatusPropType]),
}

function ReactionTimes(props) {
    return (
        <>
            <Segment>
                <Label attached="top" size="large">
                    Desired metric response times
                </Label>
                <Grid stackable>
                    <Grid.Row columns={4}>
                        <Grid.Column>
                            <DesiredResponseTimeInput status="unknown" {...props} />
                        </Grid.Column>
                        <Grid.Column>
                            <DesiredResponseTimeInput status="target_not_met" {...props} />
                        </Grid.Column>
                        <Grid.Column>
                            <DesiredResponseTimeInput status="near_target_met" {...props} />
                        </Grid.Column>
                        <Grid.Column>
                            <DesiredResponseTimeInput hoverableLabel status="debt_target_met" {...props} />
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
                            <DesiredResponseTimeInput status="confirmed" {...props} />
                        </Grid.Column>
                        <Grid.Column>
                            <DesiredResponseTimeInput status="fixed" {...props} />
                        </Grid.Column>
                        <Grid.Column>
                            <DesiredResponseTimeInput status="false_positive" {...props} />
                        </Grid.Column>
                        <Grid.Column>
                            <DesiredResponseTimeInput status="wont_fix" {...props} />
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
