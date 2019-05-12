import React from 'react';
import { Header } from 'semantic-ui-react';
import { SingleChoiceInput } from './fields/SingleChoiceInput';

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
            label="Subject type"
            options={options}
            readOnly={props.readOnly}
            set_value={(value) => props.set_value(value)}
            value={props.subject_type}
        />
    );
}
