import React from 'react';
import { Grid, Menu, Tab } from 'semantic-ui-react';
import { StringInput } from '../fields/StringInput';
import { SubjectType } from './SubjectType';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { DeleteButton, ReorderButtonGroup } from '../widgets/Button';
import { ChangeLog } from '../changelog/ChangeLog';
import { delete_subject, set_subject_attribute } from '../api/subject';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { FocusableTab } from '../widgets/FocusableTab';

function SubjectTypeAndName({ datamodel, subject, subject_uuid, subject_name, reload }) {
    return (
        <Grid stackable>
            <Grid.Row columns={2}>
                <Grid.Column>
                    <SubjectType
                        id="subject-type"
                        datamodel={datamodel}
                        set_value={(value) => set_subject_attribute(subject_uuid, "type", value, reload)}
                        subject_type={subject.type}
                    />
                </Grid.Column>
                <Grid.Column>
                    <StringInput
                        id="subject-name"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label="Subject name"
                        placeholder={subject_name}
                        set_value={(value) => set_subject_attribute(subject_uuid, "name", value, reload)}
                        value={subject.name}
                    />
                </Grid.Column>
            </Grid.Row>
        </Grid>
    )
}

function ButtonRow({ subject_uuid, first_subject, last_subject, reload }) {
    return (
        <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
            <>
                <ReorderButtonGroup
                    first={first_subject} last={last_subject} moveable="subject"
                    onClick={(direction) => { set_subject_attribute(subject_uuid, "position", direction, reload) }} />
                <DeleteButton item_type="subject" onClick={() => delete_subject(subject_uuid, reload)} />
            </>
        } />
    )
}

export function SubjectTitle({ datamodel, report, subject, subject_uuid, first_subject, last_subject, reload }) {
    const current_subject_type = datamodel.subjects[subject.type] || { name: "Unknown subject type" };
    const subject_name = subject.name || current_subject_type.name;
    const panes = [
        { menuItem: <Menu.Item key="type_and_name"><FocusableTab>{"Subject type and name"}</FocusableTab></Menu.Item>, render: () => <Tab.Pane><SubjectTypeAndName datamodel={datamodel} subject={subject} subject_uuid={subject_uuid} subject_name={subject_name} reload={reload} /></Tab.Pane> },
        { menuItem: <Menu.Item key="changelog"><FocusableTab>{"Changelog"}</FocusableTab></Menu.Item>, render: () => <Tab.Pane><ChangeLog report_uuid={report.report_uuid} subject_uuid={subject_uuid} timestamp={report.timestamp} /></Tab.Pane> }
    ];
    return (
        <HeaderWithDetails level="h2" header={subject_name} style={{ marginTop: 50 }}>
            <Tab panes={panes} />
            <div style={{ marginTop: "20px" }}>
                <ButtonRow subject_uuid={subject_uuid} first_subject={first_subject} last_subject={last_subject} reload={reload} />
            </div>
        </HeaderWithDetails>
    )
}
