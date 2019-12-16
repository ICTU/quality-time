import React, { useEffect, useState } from 'react';
import { Form, Label } from 'semantic-ui-react';
import { ReadOnlyContext } from '../context/ReadOnly';

export function IntegerInput(props) {
    let { prefix, set_value, unit, ...otherProps } = props;
    const [value, setValue] = useState(props.value || 0)
    useEffect(() => setValue(props.value || 0), [props.value]);
    return (
        <Form onSubmit={() => { if (value !== (props.value || 0)) { props.set_value(value) } }}>
            <Form.Group style={{ marginBottom: '0px' }}>
                <ReadOnlyContext.Consumer>{(readOnly) => (
                    <Form.Input
                        {...otherProps}
                        fluid
                        focus
                        labelPosition="right"
                        onBlur={() => { if (value !== (props.value || 0)) { props.set_value(value) } }}
                        onChange={(event) => setValue(event.target.value || 0)}
                        onKeyDown={(event) => { if (event.key === "Escape") { setValue(props.value || 0) } }}
                        onSubmit={() => { if (value !== (props.value || 0)) { props.set_value(value) } }}
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
