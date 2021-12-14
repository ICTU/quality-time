import React from 'react';
import { Form } from 'semantic-ui-react';
import { ReadOnlyOrEditable } from '../context/Permissions';
import { Input } from './Input';
import { ReadOnlyInput } from './ReadOnlyInput';

export function PasswordInput(props) {
    // We shouldn't have received a real password from the backend, but ignore the password value anyway to be sure
    const { requiredPermissions, value, ...otherProps } = props;
    otherProps["value"] = value ? "*".repeat(value.length) : "";
    return <ReadOnlyOrEditable
        requiredPermissions={requiredPermissions}
        readOnlyComponent={<Form><ReadOnlyInput {...otherProps} type="password" /></Form>}
        editableComponent={<Input {...otherProps} autoComplete="new-password" type="password" />}
    />
}