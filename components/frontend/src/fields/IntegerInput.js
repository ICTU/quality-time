import React, { useEffect, useState } from 'react';
import { Form, Label } from 'semantic-ui-react';
import { ReadOnlyContext } from '../context/ReadOnly';

export function IntegerInput(props) {
    let { prefix, set_value, unit, ...otherProps } = props;
    const [value, setValue] = useState(props.value || 0)
    useEffect(() => setValue(props.value || 0), [props.value]);

    function is_valid(a_value) {
        if (props.min !== null && props.max !== null) {
            return (Number(props.min) <= Number(a_value)) && (Number(a_value) <= Number(props.max))
        }
        if (props.min !== null) {
            return Number(props.min) <= Number(a_value)
        }
        if (props.max !== null) {
            return Number(a_value) <= Number(props.max)
        }
        return true
    }

    function submit_if_changed_and_valid() {
        if (value !== (props.value || 0) && is_valid(value)) {
            props.set_value(value)
        }
    }

    return (
        <Form onSubmit={() => { submit_if_changed_and_valid() } }>
            <Form.Group style={{ marginBottom: '0px' }}>
                <ReadOnlyContext.Consumer>{(readOnly) => (
                    <Form.Input
                        {...otherProps}
                        error={!is_valid(value)}
                        fluid
                        focus
                        labelPosition="right"
                        onBlur={() => { submit_if_changed_and_valid() }}
                        onChange={(event) => { if (is_valid(event.target.value)) { setValue(event.target.value) } }}
                        onKeyDown={(event) => { if (event.key === "Escape") { setValue(props.value || 0) } }}
                        onSubmit={() => { submit_if_changed_and_valid() }}
                        readOnly={readOnly}
                        type="number"
                        value={value}
                        width={16}
                    >
                        {prefix ? <Label basic>{prefix}</Label> : null}
                        <input />
                        <Label basic>{unit}</Label>
                    </Form.Input>)}
                </ReadOnlyContext.Consumer>
            </Form.Group>
        </Form>
    )
}
