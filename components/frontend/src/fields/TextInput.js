import React, { useEffect, useState } from 'react';
import { Form } from 'semantic-ui-react';
import { ReadOnlyContext } from '../context/ReadOnly';
import { CheckableLabel } from './CheckableLabel';

export function TextInput(props) {
  let { allow_mass_edit, mass_edit_label, required, set_value, ...otherProps } = props;
  const [text, setText] = useState(props.value || '');
  useEffect(() => setText(props.value || ''), [props.value]);
  const [mass_edit, setMassEdit] = useState(false);
  return (
    <Form onSubmit={() => { if (text !== (props.value || '')) { props.set_value(text, mass_edit) } }}>
      <ReadOnlyContext.Consumer>{(readOnly) => (
        <Form.TextArea
          {...otherProps}
          error={required && text === ""}
          label={<CheckableLabel label={props.label} checkable={allow_mass_edit} checkbox_label={mass_edit_label} onClick={() => setMassEdit(true)} />}
          onBlur={() => { if (text !== (props.value || '')) { props.set_value(text, mass_edit) } }}
          onChange={(event) => setText(event.target.value)}
          onKeyDown={(event) => { if (event.key === "Escape") { setText(props.value || '') } }}
          onKeyPress={(event) => {
            if (event.key === "Enter" && event.shiftKey && text !== (props.value || '')) {
              event.preventDefault();
              props.set_value(text, mass_edit);
            }
          }}
          readOnly={readOnly}
          value={text}
        />)}
      </ReadOnlyContext.Consumer>
    </Form>
  )
}
