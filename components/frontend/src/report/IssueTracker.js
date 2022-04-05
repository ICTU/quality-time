import React, { useContext } from 'react';
import { Grid, Header, Icon } from 'semantic-ui-react';
import { StringInput } from '../fields/StringInput';
import { HyperLink } from '../widgets/HyperLink';
import { set_report_issue_tracker_attribute } from '../api/report';
import { EDIT_REPORT_PERMISSION } from '../context/Permissions';
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
    var privateTokenLabel = "Private token";
    if (report.issue_tracker) {
        const help_url = dataModel.sources[report.issue_tracker?.type]?.parameters?.private_token?.help_url;
        if (help_url) {
            privateTokenLabel = <label>{privateTokenLabel} <HyperLink url={help_url}><Icon name="help circle" link /></HyperLink></label>
        }
    }
    const report_uuid = report.report_uuid;

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
        </Grid>
    )
}
