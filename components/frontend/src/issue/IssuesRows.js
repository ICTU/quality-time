import { useState } from 'react';
import PropTypes from 'prop-types';
import { Grid } from 'semantic-ui-react';
import { set_metric_attribute, add_metric_issue } from '../api/metric';
import { get_report_issue_tracker_suggestions } from '../api/report';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { MultipleChoiceInput } from '../fields/MultipleChoiceInput';
import { ActionButton } from '../widgets/Button';
import { LabelWithHelp } from '../widgets/LabelWithHelp';
import { ErrorMessage } from '../errorMessage';
import { getMetricIssueIds } from '../utils';
import { metricPropType, reportPropType } from '../sharedPropTypes';

function CreateIssueButton({ issueTrackerConfigured, issueTrackerInstruction, metric_uuid, target, reload }) {
    return (
        <ActionButton
            action='Create new'
            disabled={!issueTrackerConfigured}
            fluid
            icon='plus'
            item_type='issue'
            onClick={() => add_metric_issue(metric_uuid, reload)}
            popup={<>Create a new issue for this {target} in the configured issue tracker and add its identifier to the tracked issue identifiers.{issueTrackerInstruction}</>}
            position='top center'
        />
    )
}
CreateIssueButton.propTypes = {
    issueTrackerConfigured: PropTypes.bool,
    issueTrackerInstruction: PropTypes.node,
    metric_uuid: PropTypes.string,
    target: PropTypes.string,
    reload: PropTypes.func
}

function IssueIdentifiers({ entityKey, issueTrackerInstruction, metric, metric_uuid, report_uuid, target, reload }) {
    const issueStatusHelp = (
        <>
            <p>Identifiers of issues in the configured issue tracker that track the progress of fixing this {target}.</p>
            <p>When the issues have all been resolved, or the technical debt end date has passed, whichever happens first, the technical debt should be resolved and the technical debt target is no longer evaluated.</p>
            {issueTrackerInstruction}
        </>
    )
    const [suggestions, setSuggestions] = useState([]);
    const labelId = `issue-identifiers-label-${metric_uuid}`
    const issue_ids = getMetricIssueIds(metric, entityKey);
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
            label={<LabelWithHelp labelId={labelId} label="Issue identifiers" help={issueStatusHelp} />}
            options={suggestions}
            set_value={(value) => set_metric_attribute(metric_uuid, "issue_ids", value, reload)}
            value={issue_ids}
            key={issue_ids}  // Make sure the multiple choice input is rerendered when the issue ids change
        />
    )
}
IssueIdentifiers.propTypes = {
    entityKey: PropTypes.string,
    issueTrackerInstruction: PropTypes.node,
    metric: metricPropType,
    metric_uuid: PropTypes.string,
    report_uuid: PropTypes.string,
    target: PropTypes.string,
    reload: PropTypes.func
}

export function IssuesRows({ metric, metric_uuid, reload, report, target }) {
    const parameters = report?.issue_tracker?.parameters;
    const issueTrackerConfigured = Boolean(report?.issue_tracker?.type && parameters?.url && parameters?.project_key && parameters?.issue_type);
    const issueTrackerInstruction = issueTrackerConfigured ? null : <p>Please configure an issue tracker by expanding the report title, selecting the 'Issue tracker' tab, and configuring an issue tracker.</p>;
    const issueIdentifiersProps = {
        issueTrackerInstruction: issueTrackerInstruction,
        metric: metric,
        metric_uuid: metric_uuid,
        report_uuid: report.report_uuid,
        target: target ?? "metric",
        reload: reload
    }
    return (
        <>
            <Grid.Row>
                <ReadOnlyOrEditable
                    requiredPermissions={[EDIT_REPORT_PERMISSION]}
                    readOnlyComponent={
                        <Grid.Column width={16}>
                            <IssueIdentifiers {...issueIdentifiersProps} />
                        </Grid.Column>
                    }
                    editableComponent={
                        <>
                            <Grid.Column width={3} verticalAlign="bottom">
                                <CreateIssueButton
                                    issueTrackerConfigured={issueTrackerConfigured}
                                    issueTrackerInstruction={issueTrackerInstruction}
                                    metric_uuid={metric_uuid}
                                    target={target ?? "metric"}
                                    reload={reload}
                                />
                            </Grid.Column>
                            <Grid.Column width={13}>
                                <IssueIdentifiers {...issueIdentifiersProps} />
                            </Grid.Column>
                        </>
                    }
                />
            </Grid.Row>
            {(getMetricIssueIds(metric).length > 0 && !issueTrackerConfigured) &&
                <Grid.Row>
                    <Grid.Column width={16}>
                        <ErrorMessage title="No issue tracker configured" message={issueTrackerInstruction} />
                    </Grid.Column>
                </Grid.Row>
            }
            {(metric.issue_status ?? []).filter((issue_status => issue_status.connection_error)).map((issue_status) =>
                <Grid.Row key={issue_status.issue_id}>
                    <Grid.Column width={16}>
                        <ErrorMessage
                            key={issue_status.issue_id}
                            title={"Connection error while retrieving " + issue_status.issue_id}
                            message={issue_status.connection_error}
                        />
                    </Grid.Column>
                </Grid.Row>
            )}
            {(metric.issue_status ?? []).filter((issue_status => issue_status.parse_error)).map((issue_status) =>
                <Grid.Row key={issue_status.issue_id}>
                    <Grid.Column width={16}>
                        <ErrorMessage
                            key={issue_status.issue_id}
                            title={"Parse error while processing " + issue_status.issue_id}
                            message={issue_status.parse_error}
                        />
                    </Grid.Column>
                </Grid.Row>
            )}
        </>
    )
}
IssuesRows.propTypes = {
    entityKey: PropTypes.string,
    metric: metricPropType,
    metric_uuid: PropTypes.string,
    reload: PropTypes.func,
    report: reportPropType,
    target: PropTypes.string,
}