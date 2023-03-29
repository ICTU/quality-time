import React, { useState } from 'react';
import { Grid } from 'semantic-ui-react';
import { Icon, Popup } from '../semantic_ui_react_wrappers';
import { get_report_issue_tracker_suggestions } from '../api/report';
import { MultipleChoiceInput } from '../fields/MultipleChoiceInput';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { Comment } from '../fields/Comment';
import { set_metric_attribute, set_metric_debt, add_metric_issue } from '../api/metric';
import { DateInput } from '../fields/DateInput';
import { ActionButton } from '../widgets/Button';
import { HyperLink } from '../widgets/HyperLink';
import { ErrorMessage } from '../errorMessage';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { get_metric_issue_ids } from '../utils';
import { Target } from './Target';
import TimeAgo from 'react-timeago'


function AcceptTechnicalDebt({ metric, metric_uuid, reload }) {
    const labelId = `accept-debt-label-${metric_uuid}`
    return (
        <SingleChoiceInput
            aria-labelledby={labelId}
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label={<label id={labelId}>Accept technical debt? <HyperLink url="https://en.wikipedia.org/wiki/Technical_debt"><Icon tabIndex="0" name="help circle" link /></HyperLink></label>}
            value={metric.accept_debt ? "yes" : "no"}
            options={[
                { key: "yes", text: "Yes", value: "yes" },
                { key: "yes_completely", text: "Yes, and also set technical debt target and end date", value: "yes_completely" },
                { key: "no", text: "No", value: "no" },
                { key: "no_completely", text: "No, and also clear technical debt target and end date", value: "no_completely" }
            ]}
            set_value={(value) => {
                const acceptDebt = value.startsWith("yes")
                if (value.endsWith("completely")) {
                    set_metric_debt(metric_uuid, acceptDebt, reload)
                } else {
                    set_metric_attribute(metric_uuid, "accept_debt", acceptDebt, reload)
                }
            }}
        />
    )
}

function TechnicalDebtEndDate({ metric, metric_uuid, reload }) {
    const labelId = `technical-debt-end-date-label-${metric_uuid}`
    const help = (
        <>
            <p>Accept technical debt until this date.</p>
            <p>After this date, or when the issues below have all been resolved, whichever happens first, the technical debt should be resolved and the technical debt target is no longer evaluated.</p>
        </>
    )
    return (
        <DateInput
            ariaLabelledBy={labelId}
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label=<InformativeDateLabel current_value_date={metric.debt_end_date} labelId={labelId} help={help}/>
            placeholder="YYYY-MM-DD"
            set_value={(value) => set_metric_attribute(metric_uuid, "debt_end_date", value, reload)}
            value={metric.debt_end_date ?? ""}
        />
    )
}

function InformativeDateLabel({current_value_date, labelId, help }){
    if (current_value_date) {
        var numberOfDays = (<TimeAgo date={current_value_date} />)
    } else {
        var numberOfDays =""
    }
    return (
        <label id={labelId}>
            Technical debt end date{numberOfDays && <span> ({numberOfDays})</span>}{" "}
            <Popup
                on={["hover", "focus"]}
                content={help}
                trigger={<Icon tabIndex="0" name="help circle" />}
            />
        </label>
    );
}

function IssueIdentifiers({ issue_tracker_instruction, metric, metric_uuid, report_uuid, reload }) {
    const issueStatusHelp = (
        <>
            <p>Identifiers of issues in the configured issue tracker that track the progress of fixing this metric.</p>
            <p>When the issues have all been resolved, or the technical debt end date has passed, whichever happens first, the technical debt should be resolved and the technical debt target is no longer evaluated.</p>
            {issue_tracker_instruction}
        </>
    )
    const [suggestions, setSuggestions] = useState([]);
    const labelId = `issue-identifiers-label-${metric_uuid}`
    const issue_ids = get_metric_issue_ids(metric);
    return (
        <MultipleChoiceInput
            aria-labelledby={labelId}
            allowAdditions
            onSearchChange={(query) => {
                if (query) {
                    get_report_issue_tracker_suggestions(report_uuid, query).then((suggestionsResponse) => {
                        const suggestionOptions = suggestionsResponse.suggestions.map((s) => ({ key: s.key, text: `${s.key}: ${s.text}`, value: s.key }))
                        setSuggestions(suggestionOptions)
                    })
                } else {
                    setSuggestions([])
                }
            }}
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label={<label id={labelId}>Issue identifiers <Popup on={['hover', 'focus']} content={issueStatusHelp} trigger={<Icon tabIndex="0" name="help circle" />} /></label>}
            options={suggestions}
            set_value={(value) => set_metric_attribute(metric_uuid, "issue_ids", value, reload)}
            value={issue_ids}
            key={issue_ids}  // Make sure the multiple choice input is rerendered when the issue ids change
        />
    )
}


export function MetricDebtParameters({ report, metric, metric_uuid, reload }) {
    const parameters = report?.issue_tracker?.parameters;
    const issueTrackerConfigured = report?.issue_tracker?.type && parameters?.url && parameters?.project_key && parameters?.issue_type;
    const issueTrackerInstruction = issueTrackerConfigured ? null : <p>Please configure an issue tracker by expanding the report title, selecting the 'Issue tracker' tab, and configuring an issue tracker.</p>;
    return (
        <Grid stackable columns={3}>
            <Grid.Row>
                <Grid.Column>
                    <AcceptTechnicalDebt metric={metric} metric_uuid={metric_uuid} reload={reload} />
                </Grid.Column>
                <Grid.Column>
                    <Target key={metric.debt_target} label="Technical debt target" labelPosition='top center' target_type="debt_target" metric={metric} metric_uuid={metric_uuid} reload={reload} />
                </Grid.Column>
                <Grid.Column>
                    <TechnicalDebtEndDate metric={metric} metric_uuid={metric_uuid} reload={reload} />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row>
                <ReadOnlyOrEditable
                    requiredPermissions={[EDIT_REPORT_PERMISSION]}
                    readOnlyComponent={
                        <Grid.Column width={16}>
                            <IssueIdentifiers issue_tracker_instruction={issueTrackerInstruction} metric={metric} metric_uuid={metric_uuid} report_uuid={report.report_uuid} reload={reload} />
                        </Grid.Column>
                    }
                    editableComponent={
                        <>
                            < Grid.Column width={3} verticalAlign="bottom">
                                <ActionButton
                                    action='Create new'
                                    disabled={!issueTrackerConfigured}
                                    fluid
                                    icon='plus'
                                    item_type='issue'
                                    onClick={() => add_metric_issue(metric_uuid, reload)}
                                    popup={<p>Create a new issue for this metric in the configured issue tracker and add its identifier to the tracked issue identifiers.{issueTrackerInstruction}</p>}
                                    position='top center'
                                />
                            </Grid.Column>
                            <Grid.Column width={13}>
                                <IssueIdentifiers issue_tracker_instruction={issueTrackerInstruction} metric={metric} metric_uuid={metric_uuid} report_uuid={report.report_uuid} reload={reload} />
                            </Grid.Column>
                        </>
                    }
                />
            </Grid.Row>
            {(get_metric_issue_ids(metric).length > 0 && !issueTrackerConfigured) &&
                <Grid.Row>
                    <Grid.Column width={16}>
                        <ErrorMessage title="No issue tracker configured" message={issueTrackerInstruction} />
                    </Grid.Column>
                </Grid.Row>
            }
            {(metric.issue_status ?? []).filter((issue_status => issue_status.connection_error)).map((issue_status) =>
                <Grid.Row key={issue_status.issue_id}>
                    <Grid.Column width={16}>
                        <ErrorMessage key={issue_status.issue_id} title={"Connection error while retrieving " + issue_status.issue_id} message={issue_status.connection_error} />
                    </Grid.Column>
                </Grid.Row>
            )}
            {(metric.issue_status ?? []).filter((issue_status => issue_status.parse_error)).map((issue_status) =>
                <Grid.Row key={issue_status.issue_id}>
                    <Grid.Column width={16}>
                        <ErrorMessage key={issue_status.issue_id} title={"Parse error while processing " + issue_status.issue_id} message={issue_status.parse_error} />
                    </Grid.Column>
                </Grid.Row>
            )}
            <Grid.Row>
                <Grid.Column width={16}>
                    <Comment
                        set_value={(value) => set_metric_attribute(metric_uuid, "comment", value, reload)}
                        value={metric.comment}
                    />
                </Grid.Column>
            </Grid.Row>
        </Grid>
    );
}
