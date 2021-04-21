import React from 'react';
import { Header } from 'semantic-ui-react';
import { EDIT_REPORT_PERMISSION } from '../context/ReadOnly';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';

export function SubjectType(props) {
    let options = [];
    Object.keys(props.datamodel.subjects).forEach((key) => {
        const subject_type = props.datamodel.subjects[key];
        options.push({
            key: key, text: subject_type.name, value: key,
            content: <Header as="h4" content={subject_type.name} subheader={subject_type.description} />
        });
    });
    return (
        <SingleChoiceInput
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label="Subject type"
            options={options}
            set_value={(value) => props.set_value(value)}
            value={props.subject_type}
        />
    );
}
