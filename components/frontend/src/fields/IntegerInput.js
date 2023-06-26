import React, { useState } from 'react';
import { Form, Label } from '../semantic_ui_react_wrappers';
import { ReadOnlyOrEditable } from '../context/Permissions';
import { ReadOnlyInput } from './ReadOnlyInput';

function EditableIntegerInput(props) {
    let { allowEmpty, editableLabel, label, min, prefix, set_value, unit, ...otherProps } = props;
    const initialValue = allowEmpty ? props.value : props.value || 0;
    const [value, setValue] = useState(initialValue)
    const minValue = min || 0;

    function isValid(aValue) {
        if (aValue === "") {
            return allowEmpty
        }
        if (Number.isNaN(parseInt(aValue))) {
            return false
        }
        if (Number(aValue) < Number(minValue)) {
            return false
        }
        if (props.max !== null && Number(aValue) > Number(props.max)) {
            return false
        }
        return true
    }

    function submitIfChangedAndValid() {
        if (value !== initialValue && isValid(value)) {
            set_value(value)
        }
    }

    return (
        <Form>
            <Form.Input
                {...otherProps}
                error={!isValid(value)}
                fluid
                focus
                label={editableLabel || label}
                labelPosition={unit ? "right" : "left"}
                min={minValue}
                onBlur={() => { submitIfChangedAndValid() }}
                onChange={(event) => { if (isValid(event.target.value)) { setValue(event.target.value) } }}
                onKeyDown={(event) => {
                    if (event.key === "Enter") { submitIfChangedAndValid() }
                    if (event.key === "Escape") { setValue(initialValue) }
                }}
                type="number"
                value={value}
                width={16}
            >
                {prefix ? <Label>{prefix}</Label> : null}
                <input />
                {unit ? <Label>{unit}</Label> : null}
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