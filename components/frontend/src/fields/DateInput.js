import React from 'react';
import { Form } from 'semantic-ui-react';
import { DateInput as CalendarDateInput } from 'semantic-ui-calendar-react';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/ReadOnly';
import { Input } from './Input';

function EditableDateInput(props) {
    // We don't use the minDate property because having a value < minDate can crash the date picker,
    // see https://github.com/ICTU/quality-time/issues/1534
    return (
        <Form>
            <CalendarDateInput
                clearable
                closable
                dateFormat="YYYY-MM-DD"
                disabled={false}
                error={props.required && props.value === ""}
                label={props.label}
                onChange={(event, { value }) => { if (value !== props.value) { props.set_value(value)}}}
                placeholder={props.placeholder}
                value={props.value}
            />
        </Form>
    )
}

export function DateInput(props) {
    return (
        <ReadOnlyOrEditable
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            readOnlyComponent={<Input {...props} />}
            editableComponent={<EditableDateInput {...props} label={props.editableLabel || props.label} />}
        />
    )
}
