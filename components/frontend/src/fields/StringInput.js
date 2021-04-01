import React, { useState } from 'react';
import { Form } from 'semantic-ui-react';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/ReadOnly';
import { Input } from './Input';

function StringInputWithSuggestions(props) {
  let { editableLabel, required, options, set_value, value, warning, ...otherProps } = props;
  const [string_options, setOptions] = useState(options);
  const [search_query, setSearchQuery] = useState(value || '');
  return (
    <Form>
      <Form.Dropdown
        {...otherProps}
        allowAdditions
        clearable
        error={(required && search_query === "") || (warning !== undefined && props.warning)}
        fluid
        label={editableLabel || props.label}
        onAddItem={(event, { value }) => { setOptions(prev_options => [{ text: value, value: value, key: value }, ...prev_options]) }}
        onChange={(event, { value }) => { setSearchQuery(value); if (value !== props.value) { set_value(value) } }}
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
  return options.length === 0 ? input : <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} readOnlyComponent={input} editableComponent={input_with_suggestions} />
}
