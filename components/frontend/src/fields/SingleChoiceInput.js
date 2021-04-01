import React from 'react';
import { Form } from 'semantic-ui-react';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/ReadOnly';

export function SingleChoiceInput(props) {
  const value_text = props.options.filter(({ value }) => value === props.value)[0].text;
  let { editableLabel, set_value, options, sort, ...otherProps } = props;

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
        requiredPermissions={[EDIT_REPORT_PERMISSION]}
        readOnlyComponent={<Form.Input {...otherProps} value={value_text} />}
        editableComponent={<Dropdown />} />
    </Form>
  )
}
