import React, { useState } from 'react';
import { DateInput } from 'semantic-ui-calendar-react';

export function DatePicker(props) {
    const [date, setDate] = useState(props.value);
    const today = new Date();
    const today_string = today.getDate() + '-' + (today.getMonth() + 1) + '-' + today.getFullYear();
    function onChange(event, { name, value}) {
        setDate(value);
        if (/^\d{1,2}-\d{1,2}-\d{4}$/.test(value))
        {
            const milliseconds_since_epoch = Date.parse(value);
            if (!isNaN(milliseconds_since_epoch)) {
                props.onDate(event, { name, value });  // We have a valid date, invoke callback
            }
        }
    }
    function onClear(event, { name, value }) {
        setDate("");
        props.onDate(event, { name, value });
    }
    return (
        <DateInput
            animation="none"  // Work-around for https://github.com/arfedulov/semantic-ui-calendar-react/issues/152
            clearable
            closable
            iconPosition="left"
            initialDate={today}
            maxDate={today}
            name={props.name}
            onChange={onChange}
            onClear={onClear}
            placeholder={today_string}
            value={date}
            aria-label={props.label}
        />
    )
}
