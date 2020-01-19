import React, { useEffect, useState } from 'react';
import { Form } from 'semantic-ui-react';
import { ReadOnlyContext } from '../context/ReadOnly';

export function TextInput(props) {
  let { editableLabel, required, set_value, ...otherProps } = props;
  const [text, setText] = useState(props.value || '');
  useEffect(() => setText(props.value || ''), [props.value]);
  return (
    <Form onSubmit={() => { if (text !== (props.value || '')) { props.set_value(text) } }}>
      <ReadOnlyContext.Consumer>{(readOnly) => (
        <Form.TextArea
          {...otherProps}
          error={required && text === ""}
          label={readOnly ? props.label : editableLabel}
          onBlur={() => { if (text !== (props.value || '')) { props.set_value(text) } }}
          onChange={(event) => setText(event.target.value)}
          onKeyDown={(event) => { if (event.key === "Escape") { setText(props.value || '') } }}
          onKeyPress={(event) => {
            if (event.key === "Enter" && event.shiftKey && text !== (props.value || '')) {
              event.preventDefault();
              props.set_value(text);
            }
          }}
          readOnly={readOnly}
          value={text}
        />)}
      </ReadOnlyContext.Consumer>
    </Form>
  )
}
