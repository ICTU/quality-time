import React, { useEffect, useState } from 'react';
import { Form, Label } from 'semantic-ui-react';
import { ReadOnlyContext } from '../context/ReadOnly';

export function Input(props) {
  let { prefix, required, set_value, ...otherProps } = props;
  const [value, setValue] = useState(props.value || "");
  useEffect(() => setValue(props.value || ''), [props.value]);
  return (
    <Form>
      <ReadOnlyContext.Consumer>{(readOnly) => (
        <Form.Input
          {...otherProps}
          error={required && value === ""}
          fluid
          focus
          labelPosition="left"
          onBlur={() => { if (value !== (props.value || "")) { set_value(value) } }}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Escape") { setValue(props.value || "") }
            if (event.key === "Enter" && value !== (props.value || "")) { set_value(value) }
          }}
          readOnly={readOnly}
          value={value}
        >
          {prefix ? <Label basic>{prefix}</Label> : null}
          <input />
        </Form.Input>)}
      </ReadOnlyContext.Consumer>
    </Form>
  )
}
