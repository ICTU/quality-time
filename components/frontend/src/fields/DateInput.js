import React, { useContext } from 'react';
import { Form } from '../semantic_ui_react_wrappers';
import SemanticDatepicker from 'react-semantic-ui-datepickers';
import 'react-semantic-ui-datepickers/dist/react-semantic-ui-datepickers.css';
import { ReadOnlyOrEditable } from '../context/Permissions';
import { ReadOnlyInput } from './ReadOnlyInput';
import { DarkMode } from '../context/DarkMode';
import './DateInput.css';

function EditableDateInput({ ariaLabelledBy, label, placeholder, required, set_value, value }) {
    value = value ? new Date(value) : null
    return (
        <SemanticDatepicker
            aria-labelledby={ariaLabelledBy}
            clearable={!required}
            error={(required && !value)}
            inverted={useContext(DarkMode)}
            label={label}
            onChange={(event, { value: newDate }) => {
                let dateValue = null
                if (!!newDate) {
                    dateValue = `${String(newDate.getFullYear())}-${String(newDate.getMonth() + 1).padStart(2, '0')}-${String(newDate.getDate()).padStart(2, '0')}`;
                }
                set_value(dateValue)
            }}
            placeholder={placeholder}
            value={value}
        />
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
