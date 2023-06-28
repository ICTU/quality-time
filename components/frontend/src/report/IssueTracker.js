import React, { useContext, useEffect, useState } from 'react';
import { Grid, Header, Message } from 'semantic-ui-react';
import { LabelWithHelp } from '../widgets/LabelWithHelp';
import { LabelWithHyperLink } from '../widgets/LabelWithHyperLink';
import { get_report_issue_tracker_options, set_report_issue_tracker_attribute } from '../api/report';
import { EDIT_REPORT_PERMISSION } from '../context/Permissions';
import { StringInput } from '../fields/StringInput';
import { MultipleChoiceInput } from '../fields/MultipleChoiceInput';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { PasswordInput } from '../fields/PasswordInput';
import { Logo } from '../source/Logo';
import { DataModel } from '../context/DataModel';

const NONE_OPTION = {
    key: null, text: "None", value: null, content:
        <Header as="h4">
            <Header.Content>None</Header.Content>
        </Header>
}

export function IssueTracker({ report, reload }) {
    const dataModel = useContext(DataModel)
    const [projectOptions, setProjectOptions] = useState([])  // Possible projects for new issues
    const [projectValid, setProjectValid] = useState(true)  // Is the current project a possible project?
    const [issueTypeOptions, setIssueTypeOptions] = useState([])  // Possible issue types for new issues in the current project
    const [issueTypeValid, setIssueTypeValid] = useState(true)  // Is the current issue type a possible issue type?
    const [labelFieldSupported, setLabelFieldSupported] = useState(false)  // Does the current issue type support labels?
    const [issueEpicOptions, setIssueEpicOptions] = useState([])  // Possible epic links for new issues in the current project
    const [issueEpicFieldSupported, setEpicFieldSupported] = useState(false)  // Does the current project and issue type support epic links?
    useEffect(() => {
        let didCancel = false;
        get_report_issue_tracker_options(report.report_uuid).then(function (json) {
            if (!didCancel) {
                // For projects, use the project key as value to store because that's what users entered when this wasn't a single choice option yet
                setProjectOptions(json.projects.map(({key, name}) => ({ key: key, value: key, text: name })));
                setProjectValid(json.projects.some(({key}) => (key === report.issue_tracker?.parameters?.project_key)))
                // For issue types, use the name as value to store because that's what users entered when this wasn't a single choice option yet
                setIssueTypeOptions(json.issue_types.map(({key, name}) => ({ key: key, value: name, text: name })));
                setIssueTypeValid(json.issue_types.some(({name}) => (name === report.issue_tracker?.parameters?.issue_type)))
                setIssueEpicOptions(json.epic_links.map(({key, name}) => ({ key: key, value: key, text: name })));
                const fieldKeys = json.fields.map((field) => field.key);
                setLabelFieldSupported(fieldKeys.includes("labels"))
                const fieldNames = json.fields.map((field) => field.name.toLowerCase());
                setEpicFieldSupported(fieldNames.includes("epic link"))
            }
        });
        return () => { didCancel = true; };
    }, [report])
    let trackerSources = Object.entries(dataModel.sources).filter(
        ([_source_name, source_type]) => { return source_type.issue_tracker === true }
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
    let privateTokenLabel = "Private token";
    if (report.issue_tracker) {
        const help_url = dataModel.sources[report.issue_tracker?.type]?.parameters?.private_token?.help_url;
        if (help_url) {
            privateTokenLabel = <LabelWithHyperLink label={privateTokenLabel} url={help_url} />
        }
    }
    const report_uuid = report.report_uuid;
    const project_key = report.issue_tracker?.parameters?.project_key;
    const issue_type = report.issue_tracker?.parameters?.issue_type;
    const epic_link = report.issue_tracker?.parameters?.epic_link;

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
            <Grid.Row columns={2}>
                <Grid.Column>
                    <SingleChoiceInput
                        id="tracker-project-key"
                        error={!!report.issue_tracker?.type && !projectValid}
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        required={!!report.issue_tracker?.type}
                        label={
                            <LabelWithHelp
                                label="Project for new issues"
                                help="The projects available for new issues are determined by the configured credentials"
                            />
                        }
                        options={projectOptions}
                        placeholder="None"
                        set_value={(value) => set_report_issue_tracker_attribute(report_uuid, "project_key", value, reload)}
                        value={project_key}
                    />
                </Grid.Column>
                <Grid.Column>
                    <SingleChoiceInput
                        id="tracker-issue-type"
                        error={!!report.issue_tracker?.type && !issueTypeValid}
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        required={!!report.issue_tracker?.type}
                        label={
                            <LabelWithHelp
                                label="Issue type for new issues"
                                help="The issue types available for new issues are determined by the selected project"
                            />
                        }
                        options={issueTypeOptions}
                        placeholder="None"
                        set_value={(value) => set_report_issue_tracker_attribute(report_uuid, "issue_type", value, reload)}
                        value={issue_type}
                    />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row columns={2}>
                <Grid.Column>
                    <SingleChoiceInput
                        id="tracker-issue-epic-link"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label={
                            <LabelWithHelp
                                label="Epic link for new issues"
                                help="The epics available for new issues are determined by the selected project"
                            />
                        }
                        placeholder="None"
                        options={issueEpicOptions}
                        set_value={(value) => set_report_issue_tracker_attribute(report_uuid, "epic_link", value, reload)}
                        value={epic_link}
                    />
                    {
                        project_key && issue_type && !issueEpicFieldSupported && <Message
                            warning
                            header="Epic links not supported"
                            content={`The issue type '${issue_type}' in project '${project_key}' does not support adding epic links when creating issues, so no epic link will be added to new issues.`}
                        />
                    }
                </Grid.Column>
                <Grid.Column>
                    <MultipleChoiceInput
                        allowAdditions
                        id="tracker-issue-labels"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label={
                            <LabelWithHelp
                                label="Labels for new issues"
                                help="Spaces in labels are allowed here, but they will be replaced by underscores in Jira"
                            />
                        }
                        placeholder="Enter one or more labels here"
                        set_value={(value) => set_report_issue_tracker_attribute(report_uuid, "issue_labels", value, reload)}
                        value={report.issue_tracker?.parameters?.issue_labels}
                    />
                    {
                        project_key && issue_type && !labelFieldSupported && <Message
                            warning
                            header="Labels not supported"
                            content={`The issue type '${issue_type}' in project '${project_key}' does not support adding labels when creating issues, so no labels will be added to new issues.`}
                        />
                    }
                </Grid.Column>
            </Grid.Row>
        </Grid>
    )
}
