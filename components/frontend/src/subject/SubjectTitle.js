import React from 'react';
import { Grid, Header } from 'semantic-ui-react';
import { StringInput } from '../fields/StringInput';
import { SubjectType } from './SubjectType';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { DeleteButton, ReorderButtonGroup } from '../widgets/Button';
import { ChangeLog } from '../changelog/ChangeLog';
import { delete_subject, set_subject_attribute } from '../api/subject';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';

export function SubjectTitle(props) {
    const current_subject_type = props.datamodel.subjects[props.subject.type] || { name: "Unknown subject type", description: "No description" };
    const subject_name = props.subject.name || current_subject_type.name;
    const subject_uuid = props.subject_uuid;

    function ButtonGridRow() {
        return (
            <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
                <Grid.Row>
                    <Grid.Column>
                        <ReorderButtonGroup
                            first={props.first_subject} last={props.last_subject} moveable="subject"
                            onClick={(direction) => { set_subject_attribute(subject_uuid, "position", direction, props.reload) }} />
                        <DeleteButton item_type="subject" onClick={() => delete_subject(subject_uuid, props.reload)} />
                    </Grid.Column>
                </Grid.Row>}
            />
        )
    }
    return (
        <HeaderWithDetails level="h2" header={subject_name} style={{ marginTop: 50 }}>
            <Header>
                <Header.Content>
                    {current_subject_type.name}
                    <Header.Subheader>
                        {current_subject_type.description}
                    </Header.Subheader>
                </Header.Content>
            </Header>
            <Grid stackable>
                <Grid.Row columns={3}>
                    <Grid.Column>
                        <SubjectType
                            datamodel={props.datamodel}
                            set_value={(value) => set_subject_attribute(subject_uuid, "type", value, props.reload)}
                            subject_type={props.subject.type}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <StringInput
                            requiredPermissions={[EDIT_REPORT_PERMISSION]}
                            label="Subject name"
                            placeholder={current_subject_type.name}
                            set_value={(value) => set_subject_attribute(subject_uuid, "name", value, props.reload)}
                            value={props.subject.name}
                        />
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row>
                    <Grid.Column>
                        <ChangeLog
                            report_uuid={props.report.report_uuid}
                            subject_uuid={subject_uuid}
                            timestamp={props.report.timestamp}
                        />
                    </Grid.Column>
                </Grid.Row>
                <ButtonGridRow />
            </Grid>
        </HeaderWithDetails>
    )
}
