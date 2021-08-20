import React, { useEffect, useState } from 'react';
import { DateInput } from 'semantic-ui-calendar-react-17';
import { isValidDate_DDMMYYYY } from '../utils';

export function DatePicker(props) {
    const [date, setDate] = useState(props.value);
    useEffect(() => { setDate(props.value); }, [props.value]);
    const today = new Date();
    const today_string = today.getDate() + '-' + (today.getMonth() + 1) + '-' + today.getFullYear();
    function onChange(event, { name, value }) {
        setDate(value);
        if (isValidDate_DDMMYYYY(value)) {
            props.onDate(event, { name, value });
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
