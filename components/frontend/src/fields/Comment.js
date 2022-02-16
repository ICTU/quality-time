import React from 'react';
import { EDIT_REPORT_PERMISSION } from '../context/Permissions';
import { TextInput } from './TextInput';

export function Comment(props) {
    return (
        <TextInput
            label="Comment"
            placeholder="Enter comments here (HTML allowed; URL's are transformed into links)"
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            {...props}
        />
    )
}
