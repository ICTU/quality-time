import React, { useState } from 'react';
import { Form } from 'semantic-ui-react';
import { ReadOnlyOrEditable } from '../context/ReadOnly';

function sort_options(option_list) {
  let options = new Set();
  option_list.forEach((option) => { options.add({ key: option, text: option, value: option }) });
  options = Array.from(options);
  options.sort((a, b) => a.text.localeCompare(b.text));
  return options;
}

export function MultipleChoiceInput(props) {
  let { allowAdditions, editableLabel, required, set_value, value, requiredPermissions, ...otherProps } = props;
  const choices = props.value || [];
  const [options, setOptions] = useState(props.options);
  function onChange(event, { value: changed_value }) { set_value(changed_value) }
  function onAddItem(event, { value: added_value }) { setOptions(prev_options => ([added_value, ...prev_options])) }
  function Dropdown() {
    return (
      <Form.Dropdown
        {...otherProps}
        allowAdditions={allowAdditions}
        error={required && choices.length === 0}
        fluid
        label={editableLabel || props.label}
        multiple
        onAddItem={onAddItem}
        onChange={onChange}
        options={sort_options(options)}
        search
        selection
        value={choices}
      />
    )
  }
  return (
    <Form>
      <ReadOnlyOrEditable
            requiredPermissions={requiredPermissions}
            readOnlyComponent={<Form.Input value={value ? value.join(', ') : ''} {...otherProps} />}
            editableComponent={<Dropdown />} />
    </Form>
  )
}
