import React, { useEffect, useState } from 'react';
import { Form } from 'semantic-ui-react';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { CheckableLabel } from './CheckableLabel';

function sort_options(option_list) {
  let options = new Set();
  option_list.forEach((option) => { options.add({ key: option, text: option, value: option }) });
  options = Array.from(options);
  options.sort((a, b) => a.text.localeCompare(b.text));
  return options;
}

export function MultipleChoiceInput(props) {
  let { allowAdditions, allow_mass_edit, mass_edit_label, required, set_value, ...otherProps } = props;
  const [choices, setChoices] = useState(props.value || []);
  useEffect(() => setChoices(props.value || []), [props.value]);
  const [options, setOptions] = useState(props.options);
  useEffect(() => setOptions(props.options), [props.options]);
  const [mass_edit, setMassEdit] = useState(false);
  return (
    <Form>
      <ReadOnlyOrEditable
        readOnlyComponent={<Form.Input {...otherProps} />}
        editableComponent={
          <Form.Dropdown
            {...otherProps}
            allowAdditions={allowAdditions}
            error={required && choices.length === 0}
            fluid
            label={<CheckableLabel label={props.label} checkable={allow_mass_edit} checkbox_label={mass_edit_label} onClick={() => setMassEdit(true)} />}
            multiple
            onAddItem={(event, { value }) => { setOptions(prev_options => ([value, ...prev_options])) }}
            onChange={(event, { value }) => { setChoices(value); if (value !== props.value) { set_value(value, mass_edit) } }}
            options={sort_options(options)}
            search
            selection
            value={choices}
          />
        }
      />
    </Form>
  )
}
