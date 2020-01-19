import React, { useEffect, useState } from 'react';
import { Form } from 'semantic-ui-react';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { CheckableLabel } from './CheckableLabel';

export function SingleChoiceInput(props) {
  const value_text = props.options.filter(({ value }) => value === props.value)[0].text;
  let { allow_mass_edit, mass_edit_label, set_value, options, ...otherProps } = props;
  options.sort((a, b) => a.text.localeCompare(b.text));
  const [choice, setChoice] = useState(props.value);
  useEffect(() => setChoice(props.value), [props.value]);
  const [mass_edit, setMassEdit] = useState(false);

  return (
    <Form>
      <ReadOnlyOrEditable
        readOnlyComponent={<Form.Input {...otherProps} value={value_text} />}
        editableComponent={
          <Form.Dropdown
            {...otherProps}
            fluid
            label={<CheckableLabel label={props.label} checkable={allow_mass_edit} checkbox_label={mass_edit_label} onClick={() => setMassEdit(true)} />}
            onChange={(event, { name, value }) => { setChoice(value); if (value !== props.value) { set_value(value, mass_edit) } }}
            options={options}
            search
            selection
            selectOnNavigation={false}
            tabIndex="0"
            value={choice}
          />
        }
      />
    </Form>
    )
  }
