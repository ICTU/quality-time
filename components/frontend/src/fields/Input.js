import React, { useEffect, useState } from 'react';
import { Form, Label } from 'semantic-ui-react';
import { ReadOnlyContext } from '../context/ReadOnly';
import { CheckableLabel } from './CheckableLabel';

export function Input(props) {
  let { allow_mass_edit, mass_edit_label, prefix, required, set_value, ...otherProps } = props;
  const initialValue = props.value || "";
  const [value, setValue] = useState(initialValue);
  useEffect(() => setValue(initialValue), [initialValue]);
  const [mass_edit, setMassEdit] = useState(false);

  function submit_if_changed() {
    if (value !== initialValue) { set_value(value, mass_edit) }
  }

  function onKeyDown(event) {
    if (event.key === "Escape") { setValue(initialValue) }
    if (event.key === "Enter") { submit_if_changed() }
  }

  const fixedProps = {...otherProps, error: required && value === "", fluid: true, focus: true, labelPosition: "left", value: value}
  return (
    <Form>
      <ReadOnlyContext.Consumer>{(readOnly) => (
        <Form.Input
          {...fixedProps}
          label={<CheckableLabel label={props.label} checkable={allow_mass_edit} checkbox_label={mass_edit_label} onClick={() => setMassEdit(true)} />}
          onBlur={() => { submit_if_changed() }}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={onKeyDown}
          readOnly={readOnly}
        >
          {prefix ? <Label basic>{prefix}</Label> : null}
          <input />
        </Form.Input>)}
      </ReadOnlyContext.Consumer>
    </Form>
  )
}
