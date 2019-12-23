import React, { useEffect, useState } from 'react';
import { Form, Label } from 'semantic-ui-react';
import { ReadOnlyContext } from '../context/ReadOnly';

export function Input(props) {
  let { prefix, required, set_value, ...otherProps } = props;
  const initialValue = props.value || "";
  const [value, setValue] = useState(initialValue);
  useEffect(() => setValue(initialValue), [initialValue]);

  function submit_if_changed() {
    if (value !== initialValue) { set_value(value) }
  }

  const fixedProps = {...otherProps, error: required && value === "", fluid: true, focus: true, labelPosition: "left", value: value}
  return (
    <Form>
      <ReadOnlyContext.Consumer>{(readOnly) => (
        <Form.Input
          {...fixedProps}
          onBlur={() => { submit_if_changed() }}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Escape") { setValue(initialValue) }
            if (event.key === "Enter") { submit_if_changed() }
          }}
          readOnly={readOnly}
        >
          {prefix ? <Label basic>{prefix}</Label> : null}
          <input />
        </Form.Input>)}
      </ReadOnlyContext.Consumer>
    </Form>
  )
}
