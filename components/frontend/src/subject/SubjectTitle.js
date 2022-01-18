import React, { useContext } from 'react';
import { Header, Icon, Menu, Tab } from 'semantic-ui-react';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { DeleteButton, ReorderButtonGroup } from '../widgets/Button';
import { ChangeLog } from '../changelog/ChangeLog';
import { Share } from '../share/Share';
import { delete_subject, set_subject_attribute } from '../api/subject';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { FocusableTab } from '../widgets/FocusableTab';
import { SubjectParameters } from './SubjectParameters';

function SubjectHeader({ subject_type }) {
    return (
        <Header>
            <Header.Content>
                {subject_type.name}
                <Header.Subheader>
                    {subject_type.description}
                </Header.Subheader>
            </Header.Content>
        </Header>
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

export function SubjectTitle({ report, subject, subject_uuid, first_subject, last_subject, reload }) {
    const dataModel = useContext(DataModel)
    const current_subject_type = dataModel.subjects[subject.type] || { name: "Unknown subject type" };
    const subject_name = subject.name || current_subject_type.name;
    const subjectUrl = `${window.location}#${subject_uuid}`
    const panes = [
        {
            menuItem: <Menu.Item key="configuration"><Icon name="settings" /><FocusableTab>{"Configuration"}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane><SubjectParameters subject={subject} subject_uuid={subject_uuid} subject_name={subject_name} reload={reload} /></Tab.Pane>
        },
        {
            menuItem: <Menu.Item key="changelog"><Icon name="history" /><FocusableTab>{"Changelog"}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane><ChangeLog subject_uuid={subject_uuid} timestamp={report.timestamp} /></Tab.Pane>
        },
        {
            menuItem: <Menu.Item key="share"><Icon name="share square" /><FocusableTab>{'Share'}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane><Share title="Subject permanent link" url={subjectUrl} /></Tab.Pane>
        }
    ];
    return (
        <HeaderWithDetails className="sticky" level="h2" header={subject_name} subheader={subject.subtitle} style={{ marginTop: 50 }}>
            <SubjectHeader subject_type={current_subject_type} />
            <Tab panes={panes} />
            <div style={{ marginTop: "20px" }}>
                <ButtonRow subject_uuid={subject_uuid} first_subject={first_subject} last_subject={last_subject} reload={reload} />
            </div>
        </HeaderWithDetails>
    )
}
