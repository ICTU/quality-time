import React, { useEffect, useState } from 'react';
import { Form } from 'semantic-ui-react';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { CheckableLabel } from './CheckableLabel';
import { Input } from './Input';

function StringInputWithSuggestions(props) {
  let { allow_mass_edit, mass_edit_label, required, options, set_value, value, warning, ...otherProps } = props;
  const [string_options, setOptions] = useState(options);
  useEffect(() => setOptions(props.options), [props.options]);
  const [search_query, setSearchQuery] = useState(value || '');
  useEffect(() => setSearchQuery(props.value || ''), [props.value]);
  const [mass_edit, setMassEdit] = useState(false);

  return (
    <Form>
      <Form.Dropdown
        {...otherProps}
        allowAdditions
        clearable
        error={(required && search_query === "") || (warning !== undefined && props.warning)}
        fluid
        label={<CheckableLabel label={props.label} checkable={allow_mass_edit} checkbox_label={mass_edit_label} onClick={() => setMassEdit(true)} />}
        onAddItem={(event, { value }) => { setOptions(prev_options => [{ text: value, value: value, key: value }, ...prev_options]) }}
        onChange={(event, { value }) => { setSearchQuery(value); if (value !== props.value) { set_value(value, mass_edit) } }}
        onSearchChange={(event, { searchQuery }) => { setSearchQuery(searchQuery) }}
        options={string_options}
        search
        searchQuery={search_query}
        selection
      />
    </Form>
  )
}

export function StringInput(props) {
  const options = [...(props.options || [])].sort().map((value) => ({ key: value, value: value, text: value }));
  const input = <Input {...props} />;
  const input_with_suggestions = <StringInputWithSuggestions {...props} options={options} />;
  return options.length === 0 ? input : <ReadOnlyOrEditable readOnlyComponent={input} editableComponent={input_with_suggestions} />
}
