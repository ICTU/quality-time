import React from 'react';
import { Form, Label } from '../semantic_ui_react_wrappers';

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
            {prefix ? <Label>{prefix}</Label> : null}
            <input />
            {unit ? <Label>{unit}</Label> : null}
        </Form.Input>
    )
}
