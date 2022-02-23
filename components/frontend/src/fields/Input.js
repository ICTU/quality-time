import React, { useState } from 'react';
import { Form, Label } from '../semantic_ui_react_wrappers';

export function Input(props) {
    let { editableLabel, label, error, prefix, required, set_value, warning, ...otherProps } = props;
    const initialValue = props.value || "";
    const [value, setValue] = useState(initialValue);

    function submit_if_changed() {
        if (value !== initialValue) { set_value(value) }
    }
    function onKeyDown(event) {
        if (event.key === "Escape") { setValue(initialValue) }
        if (event.key === "Enter") { submit_if_changed() }
    }
    return (
        <Form.Input
            {...otherProps}
            error={error || warning || (required && value === "")}
            fluid
            focus
            label={editableLabel || label}
            labelPosition="left"
            onBlur={() => { submit_if_changed() }}
            onChange={(event) => setValue(event.target.value)}
            onKeyDown={onKeyDown}
            value={value}
        >
            {prefix ? <Label>{prefix}</Label> : null}
            <input />
        </Form.Input>
    )
}
