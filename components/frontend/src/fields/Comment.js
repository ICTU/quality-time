import React from 'react';
import { TextInput } from './TextInput';

export function Comment(props) {
    return (
        <TextInput
            label="Comment"
            placeholder="Enter comments here (HTML allowed; URL's are transformed into links)"
            {...props}
        />
    )
}
