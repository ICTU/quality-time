import React, { useContext } from 'react';
import { Header } from 'semantic-ui-react';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION } from '../context/Permissions';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';

export function SubjectType({ subject_type, set_value }) {
    const dataModel = useContext(DataModel)
    let options = [];
    Object.keys(dataModel.subjects).forEach((key) => {
        const option_subject_type = dataModel.subjects[key];
        options.push({
            key: key, text: option_subject_type.name, value: key,
            content: <Header as="h4" content={option_subject_type.name} subheader={option_subject_type.description} />
        });
    });
    return (
        <SingleChoiceInput
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label="Subject type"
            options={options}
            set_value={(value) => set_value(value)}
            value={subject_type}
        />
    );
}
