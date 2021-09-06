import React from 'react';
import { Form } from 'semantic-ui-react';
import { ReadOnlyOrEditable } from '../context/Permissions';

export function SingleChoiceInput(props) {
  const option_value = props.options.filter(({ value }) => value === props.value)[0];
  const value_text = option_value ? option_value.text : "";
  let { editableLabel, set_value, options, sort, requiredPermissions, ...otherProps } = props;

  // default should be sorted
  if (sort || sort === undefined) {
    options.sort((a, b) => a.text.localeCompare(b.text));
  }
  
  function Dropdown() {
    return (
      <Form.Dropdown
        {...otherProps}
        fluid
        label={editableLabel || props.label}
        onChange={(event, { value }) => { set_value(value) }}
        options={options}
        search
        selection
        selectOnNavigation={false}
        tabIndex="0"
        value={props.value}
      />
    )
  }
  return (
    <Form>
      <ReadOnlyOrEditable
        requiredPermissions={requiredPermissions}
        readOnlyComponent={<Form.Input {...otherProps} value={value_text} />}
        editableComponent={<Dropdown />} />
    </Form>
  )
}
