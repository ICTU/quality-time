import React, { useState } from 'react';
import { Form } from 'semantic-ui-react';
import { accessGranted, Permissions } from '../context/Permissions';

export function TextInput(props) {
  let { editableLabel, required, set_value, requiredPermissions, ...otherProps } = props;
  const [text, setText] = useState(props.value || '');
  function readOnly(permissions) {
    return requiredPermissions ? !accessGranted(permissions, requiredPermissions) : false
  }
  function onChange(event) {
    setText(event.target.value)
  }
  function onKeyDown(event) {
    if (event.key === "Escape") {
      setText(props.value || '')
    }
  }
  function onKeyPress(event) {
    if (event.key === "Enter" && event.shiftKey && text !== (props.value || '')) {
      event.preventDefault();
      props.set_value(text);
    }
  }
  function submit() {
    if (text !== (props.value || '')) {
      props.set_value(text)
    }
  }
  return (
    <Form onSubmit={submit}>
      <Permissions.Consumer>{(permissions) => (
        <Form.TextArea
          {...otherProps}
          error={required && text === ""}
          label={readOnly(permissions) ? editableLabel || props.label : props.label}
          onBlur={submit}
          onChange={onChange}
          onKeyDown={onKeyDown}
          onKeyPress={onKeyPress}
          readOnly={readOnly(permissions)}
          style={{marginBottom: "20pt"}}
          value={text}
        />)}
      </Permissions.Consumer>
    </Form>
  )
}
