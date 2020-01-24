import React, { useState } from 'react';
import { Form, Label } from 'semantic-ui-react';
import { ReadOnlyContext } from '../context/ReadOnly';

export function IntegerInput(props) {
    let { editableLabel, prefix, set_value, unit, ...otherProps } = props;
    const initialValue = props.value || 0;
    const [value, setValue] = useState(initialValue)
    function is_valid(a_value) {
        if (Number.isNaN(parseInt(a_value))) {
            return false
        }
        if (props.min !== null && Number(a_value) < Number(props.min)) {
            return false
        }
        if (props.max !== null && Number(a_value) > Number(props.max)) {
            return false
        }
        return true
    }
    function submit_if_changed_and_valid() {
        if (value !== initialValue && is_valid(value)) {
            set_value(value)
        }
    }
    const fixedProps = { fluid: true, focus: true, labelPosition: "right", type: "number", width: 16 }
    return (
        <Form onSubmit={() => { submit_if_changed_and_valid() }}>
            <ReadOnlyContext.Consumer>{(readOnly) =>
                <Form.Input
                    {...otherProps}
                    error={!is_valid(value)}
                    label={readOnly ? props.label : editableLabel || props.label}
                    onBlur={() => { submit_if_changed_and_valid() }}
                    onChange={(event) => { if (is_valid(event.target.value)) { setValue(event.target.value) } }}
                    onKeyDown={(event) => { if (event.key === "Escape") { setValue(initialValue) } }}
                    onSubmit={() => { submit_if_changed_and_valid() }}
                    readOnly={readOnly}
                    value={value}
                    {...fixedProps}
                >
                    {prefix ? <Label basic>{prefix}</Label> : null}
                    <input />
                    <Label basic>{unit}</Label>
                </Form.Input>}
            </ReadOnlyContext.Consumer>
        </Form>
    )
}
