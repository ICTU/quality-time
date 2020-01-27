import React, { useState } from 'react';
import { Form } from 'semantic-ui-react';
import { ReadOnlyContext } from '../context/ReadOnly';

export function TextInput(props) {
  let { editableLabel, required, set_value, ...otherProps } = props;
  const [text, setText] = useState(props.value || '');
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
      <ReadOnlyContext.Consumer>{(readOnly) => (
        <Form.TextArea
          {...otherProps}
          error={required && text === ""}
          label={readOnly ? props.label : editableLabel || props.label}
          onBlur={submit}
          onChange={onChange}
          onKeyDown={onKeyDown}
          onKeyPress={onKeyPress}
          readOnly={readOnly}
          style={{marginBottom: "20pt"}}
          value={text}
        />)}
      </ReadOnlyContext.Consumer>
    </Form>
  )
}
