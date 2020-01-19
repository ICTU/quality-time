import React, { useEffect, useState } from 'react';
import { Form } from 'semantic-ui-react';
import { DateInput as CalendarDateInput } from 'semantic-ui-calendar-react';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { CheckableLabel } from './CheckableLabel';
import { Input } from './Input';

function EditableDateInput(props) {
    const [date, setDate] = useState(props.value);
    useEffect(() => setDate(props.value), [props.value]);
    const [mass_edit, setMassEdit] = useState(false);

    return (
        <Form>
            <CalendarDateInput
                closable
                dateFormat="YYYY-MM-DD"
                disabled={false}
                label={<CheckableLabel label={props.label} checkable={props.allow_mass_edit} checkbox_label={props.mass_edit_label} onClick={() => setMassEdit(true)} />}
                onChange={(event, { name, value }) => { setDate(value); if (value !== props.value) { props.set_value(value, mass_edit)}}}
                error={props.required && date === ""}
                value={date}
            />
        </Form>
    )
}

export function DateInput(props) {
    return (<ReadOnlyOrEditable readOnlyComponent={<Input {...props} />} editableComponent={<EditableDateInput {...props} />} />)
}
