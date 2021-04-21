import React, { useState } from 'react';
import { Form, Label } from 'semantic-ui-react';
import { accessGranted, ReadOnlyContext } from '../context/ReadOnly';

export function Input(props) {
  let { editableLabel, prefix, required, set_value, warning, requiredPermissions, ...otherProps } = props;
  const initialValue = props.value || "";
  const [value, setValue] = useState(initialValue);

  function readOnly(permissions) {
    return requiredPermissions ? !accessGranted(permissions, requiredPermissions) : false
  }
  function submit_if_changed() {
    if (value !== initialValue) { set_value(value) }
  }
  function onKeyDown(event) {
    if (event.key === "Escape") { setValue(initialValue) }
    if (event.key === "Enter") { submit_if_changed() }
  }
  const fixedProps = {...otherProps, error: (required && value === "") || (warning !== undefined && props.warning), fluid: true, focus: true, labelPosition: "left", value: value}
  return (
    <Form>
      <ReadOnlyContext.Consumer>{(permissions) => (
        <Form.Input
          {...fixedProps}
          label={readOnly(permissions) ? props.label : editableLabel || props.label}
          onBlur={() => { submit_if_changed() }}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={onKeyDown}
          readOnly={readOnly(permissions)}
        >
          {prefix ? <Label basic>{prefix}</Label> : null}
          <input />
        </Form.Input>)}
      </ReadOnlyContext.Consumer>
    </Form>
  )
}
