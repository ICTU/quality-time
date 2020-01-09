import React from 'react';
import { Grid, Header } from 'semantic-ui-react';
import { StringInput } from '../fields/StringInput';
import { SubjectType } from './SubjectType';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { CopyButton, DeleteButton, ReorderButtonGroup, MoveButton } from '../widgets/Button';
import { ChangeLog } from '../changelog/ChangeLog';
import { copy_subject, delete_subject, set_subject_attribute, move_subject } from '../api/subject';
import { ReadOnlyOrEditable } from '../context/ReadOnly';

export function SubjectTitle(props) {
    const current_subject_type = props.datamodel.subjects[props.subject.type] || { name: "Unknown subject type", description: "No description" };
    const subject_name = props.subject.name || current_subject_type.name;
    const subject_uuid = props.subject_uuid;

    function ButtonRow() {
        let report_options = [];
        props.reports.forEach((report) => {
            report_options.push({
                disabled: report.report_uuid === props.report.report_uuid, key: report.report_uuid,
                text: report.title, value: report.report_uuid
            })
        });
        report_options.sort((a, b) => a.text.localeCompare(b.text));
        return (
            <ReadOnlyOrEditable editableComponent={
                <Grid.Row>
                    <Grid.Column>
                        <CopyButton
                            item_type="subject"
                            onClick={() => copy_subject(subject_uuid, props.reload)}
                        />
                        <MoveButton
                            item_type="subject"
                            onClick={(target_report_uuid) => {
                                move_subject(subject_uuid, target_report_uuid, props.reload)
                            }}
                            options={report_options} />
                        <ReorderButtonGroup
                            first={props.first_subject}
                            last={props.last_subject}
                            moveable="subject"
                            onClick={(direction) => {
                                set_subject_attribute(subject_uuid, "position", direction, props.reload)
                            }}
                            slot="position"
                        />
                        <DeleteButton
                            item_type='subject'
                            onClick={() => delete_subject(subject_uuid, props.reload)}
                        />
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
                <ButtonRow />
            </Grid>
        </HeaderWithDetails>
    )
}
