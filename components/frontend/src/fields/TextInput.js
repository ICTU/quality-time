import React, { useEffect, useState } from 'react';
import { Form } from 'semantic-ui-react';

export function TextInput(props) {
  let { required, set_value, ...otherProps } = props;
  const [text, setText] = useState(props.value || '');
  useEffect(() => setText(props.value || ''), [props.value]);
  return (
    <Form onSubmit={() => { if (text !== (props.value || '')) { props.set_value(text) } }}>
      <Form.TextArea
        {...otherProps}
        error={required && text === ""}
        onBlur={() => {
          if (text !== (props.value || '')) { props.set_value(text) }
        }}
        onChange={(event) => setText(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Escape") { setText(props.value || '') }
        }}
        onKeyPress={(event) => {
          if (event.key === "Enter" && event.shiftKey && text !== (props.value || '')) {
            event.preventDefault();
            props.set_value(text);
          }
        }}
        value={text}
      />
    </Form>
  )
}
