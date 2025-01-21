import Grid from "@mui/material/Grid2"
import { bool, func, node, string } from "prop-types"
import { useContext, useState } from "react"

import { add_metric_issue, set_metric_attribute } from "../api/metric"
import { get_report_issue_tracker_suggestions } from "../api/report"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { MultipleChoiceField } from "../fields/MultipleChoiceField"
import { metricPropType, reportPropType } from "../sharedPropTypes"
import { getMetricIssueIds } from "../utils"
import { ActionButton } from "../widgets/buttons/ActionButton"
import { AddItemIcon } from "../widgets/icons"
import { showMessage } from "../widgets/toast"
import { WarningMessage } from "../widgets/WarningMessage"

function CreateIssueButton({ issueTrackerConfigured, issueTrackerInstruction, metric_uuid, target, reload }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    return (
        <ActionButton
            action="Create new"
            disabled={disabled || !issueTrackerConfigured}
            icon={<AddItemIcon />}
            itemType="issue"
            onClick={() => add_metric_issue(metric_uuid, reload)}
            popup={
                <>
                    Create a new issue for this {target} in the configured issue tracker and add its identifier to the
                    tracked issue identifiers.{issueTrackerInstruction}
                </>
            }
        />
    )
}
CreateIssueButton.propTypes = {
    issueTrackerConfigured: bool,
    issueTrackerInstruction: node,
    metric_uuid: string,
    target: string,
    reload: func,
}

function IssueIdentifiers({ entityKey, issueTrackerInstruction, metric, metric_uuid, report_uuid, target, reload }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const issueStatusHelp = `Identifiers of issues in the configured issue tracker that track the progress of fixing this ${target}.
                When the issues have all been resolved, or the technical debt end date has passed, whichever happens
                first, the technical debt should be resolved and the technical debt target is no longer evaluated.${issueTrackerInstruction ?? ""}`
    const [suggestions, setSuggestions] = useState([])
    const issueIds = getMetricIssueIds(metric, entityKey)
    return (
        <MultipleChoiceField
            allowAdditions
            disabled={disabled}
            freeSolo
            helperText={issueStatusHelp}
            key={issueIds} // Make sure the multiple choice input is rerendered when the issue ids change
            label="Issue identifiers"
            onChange={(value) => set_metric_attribute(metric_uuid, "issue_ids", value, reload)}
            onInputChange={(_event, query) => {
                if (query) {
                    get_report_issue_tracker_suggestions(report_uuid, query)
                        .then((suggestionsResponse) => {
                            const suggestionOptions = suggestionsResponse.suggestions.map((s) => ({
                                id: s.key,
                                label: `${s.key}: ${s.text}`,
                            }))
                            setSuggestions(suggestionOptions)
                            return null
                        })
                        .catch((error) => showMessage("error", "Could not fetch issue identifiers", `${error}`))
                } else {
                    setSuggestions([])
                }
            }}
            options={suggestions}
            value={issueIds}
        />
    )
}
IssueIdentifiers.propTypes = {
    entityKey: string,
    issueTrackerInstruction: node,
    metric: metricPropType,
    metric_uuid: string,
    report_uuid: string,
    target: string,
    reload: func,
}

export function IssuesRows({ metric, metric_uuid, reload, report, target }) {
    const parameters = report?.issue_tracker?.parameters
    const issueTrackerConfigured = Boolean(
        report?.issue_tracker?.type && parameters?.url && parameters?.project_key && parameters?.issue_type,
    )
    const issueTrackerInstruction = issueTrackerConfigured
        ? null
        : " Please configure an issue tracker by expanding the report title, selecting the Issue tracker tab, and configuring an issue tracker."
    const issueIdentifiersProps = {
        issueTrackerInstruction: issueTrackerInstruction,
        metric: metric,
        metric_uuid: metric_uuid,
        report_uuid: report.report_uuid,
        target: target ?? "metric",
        reload: reload,
    }
    return (
        <>
            <Grid size={{ xs: 1, sm: "auto", md: "auto" }}>
                <CreateIssueButton
                    issueTrackerConfigured={issueTrackerConfigured}
                    issueTrackerInstruction={issueTrackerInstruction}
                    metric_uuid={metric_uuid}
                    target={target ?? "metric"}
                    reload={reload}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: "grow", md: "grow" }}>
                <IssueIdentifiers {...issueIdentifiersProps} />
            </Grid>
            {getMetricIssueIds(metric).length > 0 && !issueTrackerConfigured && (
                <Grid size={{ xs: 1, sm: 3, md: 6 }}>
                    <WarningMessage title="No issue tracker configured">{issueTrackerInstruction}</WarningMessage>
                </Grid>
            )}
            {(metric.issue_status ?? [])
                .filter((issue_status) => issue_status.connection_error)
                .map((issue_status) => (
                    <Grid key={issue_status.issue_id} size={{ xs: 1, sm: 3, md: 6 }}>
                        <WarningMessage
                            key={issue_status.issue_id}
                            pre
                            title={"Connection error while retrieving " + issue_status.issue_id}
                        >
                            {issue_status.connection_error}
                        </WarningMessage>
                    </Grid>
                ))}
            {(metric.issue_status ?? [])
                .filter((issue_status) => issue_status.parse_error)
                .map((issue_status) => (
                    <Grid key={issue_status.issue_id} size={{ xs: 1, sm: 3, md: 6 }}>
                        <WarningMessage
                            key={issue_status.issue_id}
                            pre
                            title={"Parse error while processing " + issue_status.issue_id}
                        >
                            {issue_status.parse_error}
                        </WarningMessage>
                    </Grid>
                ))}
        </>
    )
}
IssuesRows.propTypes = {
    entityKey: string,
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
    report: reportPropType,
    target: string,
}
