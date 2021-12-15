import React, { useState } from 'react';
import { Form, Label } from 'semantic-ui-react';
import { ReadOnlyOrEditable } from '../context/Permissions';
import { ReadOnlyInput } from './ReadOnlyInput';

function EditableIntegerInput(props) {
    let { editableLabel, label, prefix, set_value, unit, ...otherProps } = props;
    const initialValue = props.value || 0;
    const [value, setValue] = useState(initialValue)

    function is_valid(a_value) {
        if (Number.isNaN(parseInt(a_value))) {
            return false
        }
        if (props.min !== null && Number(a_value) < Number(props.min)) {
            return false
        }
        if (props.max !== null && Number(a_value) > Number(props.max)) {
            return false
        }
        return true
    }
    function submit_if_changed_and_valid() {
        if (value !== initialValue && is_valid(value)) {
            set_value(value)
        }
    }
    return (
        <Form onSubmit={() => { submit_if_changed_and_valid() }}>
            <Form.Input
                {...otherProps}
                error={!is_valid(value)}
                fluid
                focus
                label={editableLabel || label}
                labelPosition={unit ? "right" : "left"}
                onBlur={() => { submit_if_changed_and_valid() }}
                onChange={(event) => { if (is_valid(event.target.value)) { setValue(event.target.value) } }}
                onKeyDown={(event) => { if (event.key === "Escape") { setValue(initialValue) } }}
                type="number"
                value={value}
                width={16}
            >
                {prefix ? <Label basic>{prefix}</Label> : null}
                <input />
                {unit ? <Label basic>{unit}</Label> : null}
            </Form.Input>
        </Form>
    )
}

export function IntegerInput(props) {
    let { requiredPermissions, ...otherProps } = props;
    return (
        <ReadOnlyOrEditable
            requiredPermissions={requiredPermissions}
            readOnlyComponent={<Form><ReadOnlyInput {...otherProps} /></Form>}
            editableComponent={<EditableIntegerInput {...otherProps} />} />
    )
}