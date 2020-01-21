import React from 'react';
import { Form } from 'semantic-ui-react';
import { DateInput as CalendarDateInput } from 'semantic-ui-calendar-react';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { Input } from './Input';

function EditableDateInput(props) {
    return (
        <Form>
            <CalendarDateInput
                closable
                dateFormat="YYYY-MM-DD"
                disabled={false}
                label={props.label}
                onChange={(event, { value }) => { if (value !== props.value) { props.set_value(value)}}}
                error={props.required && props.value === ""}
                value={props.value}
            />
        </Form>
    )
}

export function DateInput(props) {
    return (<ReadOnlyOrEditable readOnlyComponent={<Input {...props} />} editableComponent={<EditableDateInput {...props} label={props.editableLabel || props.label} />} />)
}
