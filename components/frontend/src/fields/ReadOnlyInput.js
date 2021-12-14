import React from 'react';
import { Form, Label } from 'semantic-ui-react';

export function ReadOnlyInput({ error, label, placeholder, prefix, required, value, type }) {
    return (
        <Form.Input
            error={error || (required && value === "")}
            fluid
            label={label}
            labelPosition="left"
            placeholder={placeholder}
            readOnly
            tabIndex={-1}
            type={type}
            value={value}
        >
            {prefix ? <Label basic>{prefix}</Label> : null}
            <input />
        </Form.Input>
    )
}
