import React from 'react';
import { Form } from 'semantic-ui-react';
import { DateInput as CalendarDateInput } from 'semantic-ui-calendar-react';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { Input } from './Input';

function EditableDateInput(props) {
    return (
        <Form>
            <CalendarDateInput
                clearable
                closable
                dateFormat="YYYY-MM-DD"
                disabled={false}
                error={props.required && props.value === ""}
                label={props.label}
                minDate={props.minDate}
                onChange={(event, { value }) => { if (value !== props.value) { props.set_value(value)}}}
                placeholder={props.placeholder}
                value={props.value}
            />
        </Form>
    )
}

export function DateInput(props) {
    const { minDate, ...readonlyProps} = props;
    return (
        <ReadOnlyOrEditable
            readOnlyComponent={<Input {...readonlyProps} />}
            editableComponent={<EditableDateInput {...props} label={props.editableLabel || props.label} />}
        />
    )
}
