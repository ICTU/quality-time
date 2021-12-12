import React from 'react';
import { Form } from 'semantic-ui-react';
import { DateInput as CalendarDateInput } from 'semantic-ui-calendar-react-17';
import { ReadOnlyOrEditable } from '../context/Permissions';
import { ReadOnlyInput } from './ReadOnlyInput';

function EditableDateInput(props) {
    // We don't use the minDate property because having a value < minDate can crash the date picker,
    // see https://github.com/ICTU/quality-time/issues/1534
    return (
        <CalendarDateInput
            clearable
            closable
            dateFormat="YYYY-MM-DD"
            disabled={false}
            error={props.required && props.value === ""}
            label={props.label}
            onChange={(event, { value }) => { if (value !== props.value) { props.set_value(value) } }}
            placeholder={props.placeholder}
            value={props.value}
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
