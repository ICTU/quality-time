import React, { useState } from 'react';
import { Form } from '../semantic_ui_react_wrappers';
import { DateInput as CalendarDateInput } from 'semantic-ui-calendar-react-17';
import { ReadOnlyOrEditable } from '../context/Permissions';
import { isValidDate_YYYYMMDD } from '../utils';
import { ReadOnlyInput } from './ReadOnlyInput';

function EditableDateInput({ ariaLabelledBy, label, placeholder, required, set_value, value }) {
    // We don't use the minDate property because having a value < minDate can crash the date picker,
    // see https://github.com/ICTU/quality-time/issues/1534
    const [date, setDate] = useState(value);
    return (
        <CalendarDateInput
            aria-labelledby={ariaLabelledBy}
            clearable
            closable
            dateFormat="YYYY-MM-DD"
            error={(required && !isValidDate_YYYYMMDD(date)) || (date !== "" && !isValidDate_YYYYMMDD(date))}
            label={label}
            onChange={(event, { value: newDate }) => {
                if (!event) { return }
                if ((date !== newDate) && isValidDate_YYYYMMDD(newDate)) {
                    set_value(newDate)
                }
                setDate(newDate)
            }}
            onClear={() => { setDate(""); set_value("") }}
            placeholder={placeholder}
            value={date}
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
