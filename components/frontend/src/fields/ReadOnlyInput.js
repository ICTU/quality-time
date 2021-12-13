import React from 'react';
import { Form, Label } from 'semantic-ui-react';

export function ReadOnlyInput({ label, placeholder, prefix, value }) {
    return (
        <Form.Input
            fluid
            label={label}
            labelPosition="left"
            placeholder={placeholder}
            readOnly
            tabIndex={-1}
            value={value}
        >
            {prefix ? <Label basic>{prefix}</Label> : null}
            <input />
        </Form.Input>
    )
}
