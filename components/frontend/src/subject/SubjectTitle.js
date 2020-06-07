import React from 'react';
import { Grid, Header } from 'semantic-ui-react';
import { StringInput } from '../fields/StringInput';
import { SubjectType } from './SubjectType';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { ItemActionButtons } from '../widgets/Button';
import { ChangeLog } from '../changelog/ChangeLog';
import { copy_subject, delete_subject, set_subject_attribute, move_subject } from '../api/subject';
import { ReadOnlyOrEditable } from '../context/ReadOnly';

function report_options(reports, current_report_uuid) {
    let options = [];
    reports.forEach((report) => {
        options.push({
            disabled: report.report_uuid === current_report_uuid, key: report.report_uuid,
            text: report.title, value: report.report_uuid
        })
    });
    options.sort((a, b) => a.text.localeCompare(b.text));
    return options;
}

export function SubjectTitle(props) {
    const current_subject_type = props.datamodel.subjects[props.subject.type] || { name: "Unknown subject type", description: "No description" };
    const subject_name = props.subject.name || current_subject_type.name;
    const subject_uuid = props.subject_uuid;

    function ButtonGridRow() {
        return (
            <ReadOnlyOrEditable editableComponent={
                <Grid.Row>
                    <Grid.Column>
                        <ItemActionButtons
                            item_type="subject"
                            first_item={props.first_subject}
                            last_item={props.last_subject}
                            onCopy={() => copy_subject(subject_uuid, props.report.report_uuid, props.reload)}
                            onDelete={() => delete_subject(subject_uuid, props.reload)}
                            onMove={(target_report_uuid) => {
                                move_subject(subject_uuid, target_report_uuid, props.reload)
                            }}
                            onReorder={(direction) => {
                                set_subject_attribute(subject_uuid, "position", direction, props.reload)
                            }}
                            options={report_options(props.reports, props.report.report_uuid)}
                            reorder_header="Report"
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
                <ButtonGridRow />
            </Grid>
        </HeaderWithDetails>
    )
}
