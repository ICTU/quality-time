import { MenuItem, Stack } from "@mui/material"
import Grid from "@mui/material/Grid2"
import { func } from "prop-types"
import { useContext, useEffect, useState } from "react"

import { get_report_issue_tracker_options, set_report_issue_tracker_attribute } from "../api/report"
import { DataModel } from "../context/DataModel"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { MultipleChoiceField } from "../fields/MultipleChoiceField"
import { TextField } from "../fields/TextField"
import { reportPropType } from "../sharedPropTypes"
import { sourceTypeOption } from "../source/SourceType"
import { Header } from "../widgets/Header"
import { HyperLink } from "../widgets/HyperLink"
import { showMessage } from "../widgets/toast"
import { WarningMessage } from "../widgets/WarningMessage"

const NONE_OPTION = {
    key: "None",
    text: "None",
    value: "None",
    content: <Header header="None" level="h4" />,
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
    useEffect(() => {
        let didCancel = false
        get_report_issue_tracker_options(report.report_uuid)
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
        .filter(([_source_name, source_type]) => {
            return source_type.issue_tracker === true
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
    const report_uuid = report.report_uuid
    const project_key = report.issue_tracker?.parameters?.project_key
    const issue_type = report.issue_tracker?.parameters?.issue_type
    const epic_link = report.issue_tracker?.parameters?.epic_link
    return (
        <Grid alignItems="flex-start" container spacing={{ xs: 1, sm: 1, md: 2 }} columns={{ xs: 1, sm: 2, md: 2 }}>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={disabled}
                    id="tracker-type"
                    label="Issue tracker type"
                    onChange={(value) => set_report_issue_tracker_attribute(report_uuid, "type", value, reload)}
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
                    disabled={disabled}
                    label="Issue tracker URL"
                    onChange={(value) => set_report_issue_tracker_attribute(report_uuid, "url", value, reload)}
                    required={!!report.issue_tracker?.type}
                    value={report.issue_tracker?.parameters?.url}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={disabled}
                    id="tracker-username"
                    label="Username for basic authentication"
                    onChange={(value) => set_report_issue_tracker_attribute(report_uuid, "username", value, reload)}
                    value={report.issue_tracker?.parameters?.username}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={disabled}
                    id="tracker-password"
                    label="Password for basic authentication"
                    onChange={(value) => set_report_issue_tracker_attribute(report_uuid, "password", value, reload)}
                    type="password"
                    value={report.issue_tracker?.parameters?.password}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={disabled}
                    id="tracker-token"
                    helperText={privateTokenHelp}
                    label="Private token"
                    onChange={(value) =>
                        set_report_issue_tracker_attribute(report_uuid, "private_token", value, reload)
                    }
                    type="password"
                    value={report.issue_tracker?.parameters?.private_token}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }} />
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={disabled}
                    error={!!report.issue_tracker?.type && project_key && !projectValid}
                    helperText="The projects available for new issues are determined by the configured credentials"
                    id="tracker-project-key"
                    label="Project for new issues"
                    required={!!report.issue_tracker?.type}
                    placeholder="None"
                    onChange={(value) => set_report_issue_tracker_attribute(report_uuid, "project_key", value, reload)}
                    select
                    value={project_key}
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
                    disabled={disabled}
                    error={!!report.issue_tracker?.type && issue_type && !issueTypeValid}
                    helperText="The issue types available for new issues are determined by the selected project"
                    id="tracker-issue-type"
                    label="Issue type for new issues"
                    onChange={(value) => set_report_issue_tracker_attribute(report_uuid, "issue_type", value, reload)}
                    placeholder="None"
                    required={!!report.issue_tracker?.type}
                    select
                    value={issue_type}
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
                        disabled={disabled}
                        helperText="The epics available for new issues are determined by the selected project"
                        id="tracker-issue-epic-link"
                        label="Epic link for new issues"
                        onChange={(value) =>
                            set_report_issue_tracker_attribute(report_uuid, "epic_link", value, reload)
                        }
                        placeholder="None"
                        select
                        value={epic_link}
                    >
                        {issueEpicOptions.map((option) => (
                            <MenuItem key={option.key} value={option.value}>
                                {option.text}
                            </MenuItem>
                        ))}
                    </TextField>
                    <WarningMessage
                        showIf={Boolean(project_key && issue_type && !issueEpicFieldSupported)}
                        title="Epic links not supported"
                    >
                        {`The issue type '${issue_type}' in project '${project_key}' does not support adding epic links when creating issues, so no epic link will be added to new issues.`}
                    </WarningMessage>
                </Stack>
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <Stack spacing={2}>
                    <MultipleChoiceField
                        disabled={disabled}
                        freeSolo
                        helperText="Spaces in labels are allowed here, but they will be replaced by underscores in Jira"
                        id="tracker-issue-labels"
                        label="Labels for new issues"
                        onChange={(value) =>
                            set_report_issue_tracker_attribute(report_uuid, "issue_labels", value, reload)
                        }
                        options={[]}
                        value={report.issue_tracker?.parameters?.issue_labels ?? []}
                    />
                    <WarningMessage
                        showIf={Boolean(project_key && issue_type && !labelFieldSupported)}
                        title="Labels not supported"
                    >
                        {`The issue type '${issue_type}' in project '${project_key}' does not support adding labels when creating issues, so no labels will be added to new issues.`}
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
