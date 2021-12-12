import React from 'react';
import { Form, Label } from 'semantic-ui-react';

export function ReadOnlyInput({ label, placeholder, prefix, value }) {
    return (
        <Form.Input
            fluid
            focus
            label={label}
            labelPosition="left"
            placeholder={placeholder}
            readOnly
            value={value}
        >
            {prefix ? <Label basic>{prefix}</Label> : null}
            <input />
        </Form.Input>
    )
}
