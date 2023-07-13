import React from 'react';
import { Icon, Label, Form } from '../semantic_ui_react_wrappers';
import { DatePicker } from '../widgets/DatePicker';
import { ReadOnlyOrEditable } from '../context/Permissions';
import { ReadOnlyInput } from './ReadOnlyInput';
import { toISODateStringInCurrentTZ } from '../utils';
import './DateInput.css';

function EditableDateInput({ ariaLabelledBy, label, placeholder, required, set_value, value }) {
    value = value ? new Date(value) : null
    return (
        <Form.Input
            aria-labelledby={ariaLabelledBy}
            error={(required && !value)}
            label={label}
            labelPosition="left"
            required={required}
        >
            <Label><Icon fitted name="calendar" /></Label>
            <DatePicker
                selected={value}
                isClearable={!required}
                onChange={(newDate) => {
                    let dateValue = null
                    if (newDate !== null) {
                        dateValue = toISODateStringInCurrentTZ(newDate)
                    }
                    set_value(dateValue)
                }}
                placeholderText={placeholder}
            />
        </Form.Input>
    )
}

export function DateInput(props) {
    return (
        <Form>
            <ReadOnlyOrEditable
                requiredPermissions={props.requiredPermissions}
                readOnlyComponent={<ReadOnlyInput {...props} />}
                editableComponent={<EditableDateInput {...props} label={props.editableLabel || props.label} />}
            />
        </Form>
    )
}
