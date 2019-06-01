import React, { useEffect, useState } from 'react';
import { Form } from 'semantic-ui-react';
import { DateInput as CalendarDateInput } from 'semantic-ui-calendar-react';
import { Input } from './Input';

function EditableDateInput(props) {
    const [date, setDate] = useState(props.value);
    useEffect(() => { props.set_value(date) }, [date]);
    return (
        <Form>
            <CalendarDateInput
                dateFormat="YYYY-MM-DD"
                disabled={props.readOnly}
                label={props.label}
                onChange={(event, { name, value }) => setDate(value)}
                error={props.required && date === ""}
                value={date}
            />
        </Form>
    )
}

export function DateInput(props) {
    return props.readOnly ?
        <Input {...props} icon='calendar' />
        :
        <EditableDateInput {...props} />
}
