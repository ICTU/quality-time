import { MenuItem, Stack } from "@mui/material"
import Grid from "@mui/material/Grid"
import { func } from "prop-types"
import { useContext, useEffect, useState } from "react"

import { getReportIssueTrackerOptions, setReportIssueTrackerAttribute } from "../api/report"
import { DataModel } from "../context/DataModel"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { MultipleChoiceField } from "../fields/MultipleChoiceField"
import { TextField } from "../fields/TextField"
import { reportPropType } from "../sharedPropTypes"
import { sourceTypeOption } from "../source/SourceType"
import { HyperLink } from "../widgets/HyperLink"
import { showMessage } from "../widgets/toast"
import { WarningMessage } from "../widgets/WarningMessage"

const NONE_OPTION = {
    key: "None",
    text: "None",
    value: "None",
    content: "None",
}

export function IssueTracker({ report, reload }) {
    const dataModel = useContext(DataModel)
    const [projectOptions, setProjectOptions] = useState([]) // Possible projects for new issues
    const [projectValid, setProjectValid] = useState(true) // Is the current project a possible project?
    const [issueTypeOptions, setIssueTypeOptions] = useState([]) // Possible issue types for new issues in the current project
    const [issueTypeValid, setIssueTypeValid] = useState(true) // Is the current issue type a possible issue type?
    const [labelFieldSupported, setLabelFieldSupported] = useState(false) // Does the current issue type support labels?
    const [issueEpicOptions, setIssueEpicOptions] = useState([]) // Possible epic links for new issues in the current project
    const [issueEpicFieldSupported, setIssueEpicFieldSupported] = useState(false) // Does the current project and issue type support epic links?
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const reportUuid = report.report_uuid
    useEffect(() => {
        let didCancel = false
        getReportIssueTrackerOptions(reportUuid)
            .then(function (json) {
                if (!didCancel) {
                    // For projects, use the project key as value to store because that's what users entered when this wasn't a single choice option yet
                    setProjectOptions(json.projects.map(({ key, name }) => ({ key: key, value: key, text: name })))
                    setProjectValid(
                        json.projects.some(({ key }) => key === report.issue_tracker?.parameters?.project_key),
                    )
                    // For issue types, use the name as value to store because that's what users entered when this wasn't a single choice option yet
                    setIssueTypeOptions(
                        json.issue_types.map(({ key, name }) => ({
                            key: key,
                            value: name,
                            text: name,
                        })),
                    )
                    setIssueTypeValid(
                        json.issue_types.some(({ name }) => name === report.issue_tracker?.parameters?.issue_type),
                    )
                    setIssueEpicOptions(json.epic_links.map(({ key, name }) => ({ key: key, value: key, text: name })))
                    const fieldKeys = json.fields.map((field) => field.key)
                    setLabelFieldSupported(fieldKeys.includes("labels"))
                    const fieldNames = json.fields.map((field) => field.name.toLowerCase())
                    setIssueEpicFieldSupported(fieldNames.includes("epic link"))
                }
                return null
            })
            .catch((error) => showMessage("error", "Could not fetch issue tracker options", `${error}`))
        return () => {
            didCancel = true
        }
    }, [report])
    let trackerSources = Object.entries(dataModel.sources)
        .filter(([_sourceName, sourceType]) => {
            return sourceType.issue_tracker === true
        })
        .map(([sourceName, sourceType]) => sourceTypeOption(sourceName, sourceType))
    trackerSources.push(NONE_OPTION)
    let privateTokenHelp = ""
    if (report.issue_tracker) {
        const helpUrl = dataModel.sources[report.issue_tracker?.type]?.parameters?.private_token?.help_url
        if (helpUrl) {
            privateTokenHelp = <HyperLink url={helpUrl}>How to configure a private token</HyperLink>
        }
    }
    const projectKey = report.issue_tracker?.parameters?.project_key
    const issueType = report.issue_tracker?.parameters?.issue_type
    const epicLink = report.issue_tracker?.parameters?.epic_link
    // The onChange handler below would erronously save the string "None" as report.issue_tracker.type. That has been
    // fixed in v5.44.0, but we have to take into account that the database may still contain "None":
    const issueTrackerFieldDisabled = disabled || !report.issue_tracker?.type || report.issue_tracker?.type === "None"
    return (
        <Grid alignItems="flex-start" container spacing={{ xs: 1, sm: 1, md: 2 }} columns={{ xs: 1, sm: 2, md: 2 }}>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={disabled}
                    id="tracker-type"
                    label="Issue tracker type"
                    onChange={(value) =>
                        setReportIssueTrackerAttribute(reportUuid, "type", value === "None" ? "" : value, reload)
                    }
                    select
                    value={report.issue_tracker?.type ?? "None"}
                >
                    {trackerSources.map((source) => (
                        <MenuItem key={source.key} value={source.value}>
                            {source.content}
                        </MenuItem>
                    ))}
                </TextField>
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    id="tracker_url"
                    disabled={issueTrackerFieldDisabled}
                    label="Issue tracker URL"
                    onChange={(value) => setReportIssueTrackerAttribute(reportUuid, "url", value, reload)}
                    required={!!report.issue_tracker?.type}
                    value={report.issue_tracker?.parameters?.url}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={issueTrackerFieldDisabled}
                    id="tracker-username"
                    label="Username for basic authentication"
                    onChange={(value) => setReportIssueTrackerAttribute(reportUuid, "username", value, reload)}
                    value={report.issue_tracker?.parameters?.username}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={issueTrackerFieldDisabled}
                    id="tracker-password"
                    label="Password for basic authentication"
                    onChange={(value) => setReportIssueTrackerAttribute(reportUuid, "password", value, reload)}
                    type="password"
                    value={report.issue_tracker?.parameters?.password}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={issueTrackerFieldDisabled}
                    id="tracker-token"
                    helperText={privateTokenHelp}
                    label="Private token"
                    onChange={(value) => setReportIssueTrackerAttribute(reportUuid, "private_token", value, reload)}
                    type="password"
                    value={report.issue_tracker?.parameters?.private_token}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }} />
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={issueTrackerFieldDisabled}
                    error={!!report.issue_tracker?.type && projectKey && !projectValid}
                    helperText="The projects available for new issues are determined by the configured credentials"
                    id="tracker-project-key"
                    label="Project for new issues"
                    required={!!report.issue_tracker?.type}
                    placeholder="None"
                    onChange={(value) => setReportIssueTrackerAttribute(reportUuid, "project_key", value, reload)}
                    select
                    value={projectKey}
                >
                    {projectOptions.map((option) => (
                        <MenuItem key={option.key} value={option.value}>
                            {option.text}
                        </MenuItem>
                    ))}
                </TextField>
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={issueTrackerFieldDisabled}
                    error={!!report.issue_tracker?.type && issueType && !issueTypeValid}
                    helperText="The issue types available for new issues are determined by the selected project"
                    id="tracker-issue-type"
                    label="Issue type for new issues"
                    onChange={(value) => setReportIssueTrackerAttribute(reportUuid, "issue_type", value, reload)}
                    placeholder="None"
                    required={!!report.issue_tracker?.type}
                    select
                    value={issueType}
                >
                    {issueTypeOptions.map((option) => (
                        <MenuItem key={option.key} value={option.value}>
                            {option.text}
                        </MenuItem>
                    ))}
                </TextField>
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <Stack spacing={2}>
                    <TextField
                        disabled={issueTrackerFieldDisabled}
                        helperText="The epics available for new issues are determined by the selected project"
                        id="tracker-issue-epic-link"
                        label="Epic link for new issues"
                        onChange={(value) => setReportIssueTrackerAttribute(reportUuid, "epic_link", value, reload)}
                        placeholder="None"
                        select
                        value={epicLink}
                    >
                        {issueEpicOptions.map((option) => (
                            <MenuItem key={option.key} value={option.value}>
                                {option.text}
                            </MenuItem>
                        ))}
                    </TextField>
                    <WarningMessage
                        showIf={Boolean(projectKey && issueType && !issueEpicFieldSupported)}
                        title="Epic links not supported"
                    >
                        {`The issue type '${issueType}' in project '${projectKey}' does not support adding epic links when creating issues, so no epic link will be added to new issues.`}
                    </WarningMessage>
                </Stack>
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <Stack spacing={2}>
                    <MultipleChoiceField
                        disabled={issueTrackerFieldDisabled}
                        freeSolo
                        helperText="Spaces in labels are allowed here, but they will be replaced by underscores in Jira"
                        id="tracker-issue-labels"
                        label="Labels for new issues"
                        onChange={(value) => setReportIssueTrackerAttribute(reportUuid, "issue_labels", value, reload)}
                        options={[]}
                        value={report.issue_tracker?.parameters?.issue_labels ?? []}
                    />
                    <WarningMessage
                        showIf={Boolean(projectKey && issueType && !labelFieldSupported)}
                        title="Labels not supported"
                    >
                        {`The issue type '${issueType}' in project '${projectKey}' does not support adding labels when creating issues, so no labels will be added to new issues.`}
                    </WarningMessage>
                </Stack>
            </Grid>
        </Grid>
    )
}
IssueTracker.propTypes = {
    reload: func,
    report: reportPropType,
}
