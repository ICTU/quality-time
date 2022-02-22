import React from 'react';
import { Label } from 'semantic-ui-react';
import { Form } from '../semantic_ui_react_wrappers/Form';

export function ReadOnlyInput({ error, label, placeholder, prefix, required, value, type, unit }) {
    return (
        <Form.Input
            error={error || (required && value === "")}
            fluid
            label={label}
            labelPosition={unit ? "right" : "left"}
            placeholder={placeholder}
            readOnly
            tabIndex={-1}
            type={type}
            value={value || ""}
        >
            {prefix ? <Label basic>{prefix}</Label> : null}
            <input />
            {unit ? <Label basic>{unit}</Label> : null}
        </Form.Input>
    )
}
