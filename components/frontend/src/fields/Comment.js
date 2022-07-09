import React from 'react';
import { useUID } from 'react-uid';
import { EDIT_REPORT_PERMISSION } from '../context/Permissions';
import { TextInput } from './TextInput';

export function Comment(props) {
    const labelId = useUID();
    return (
        <TextInput
            aria-labelledby={labelId}
            label={<label id={labelId}>Comment</label>}
            placeholder="Enter comments here (HTML allowed; URL's are transformed into links)"
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            {...props}
        />
    )
}
