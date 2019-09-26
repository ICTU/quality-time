import React, { useEffect, useState } from 'react';
import { Form } from 'semantic-ui-react';
import { Input } from './Input';

function StringInputWithSuggestions(props) {
  let { required, options, set_value, value, ...otherProps } = props;
  const [string_options, setOptions] = useState(options);
  useEffect(() => setOptions(props.options), [props.options]);
  const [search_query, setSearchQuery] = useState(value || '');
  useEffect(() => setSearchQuery(props.value || ''), [props.value]);
  return (
    <Form>
      <Form.Dropdown
        {...otherProps}
        allowAdditions
        error={(required && search_query === "") || props.warning}
        fluid
        onAddItem={(event, { value }) => { setOptions(prev_options => [{ text: value, value: value, key: value }, ...prev_options])} }
        onChange={(event, { value }) => { setSearchQuery(value); if (value !== props.value) { set_value(value) } }}
        onSearchChange={(event, { searchQuery} ) => { setSearchQuery(searchQuery) }}
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
  return props.readOnly || options.length === 0 ?
    <Input {...props} />
    :
    <StringInputWithSuggestions {...props} options={options} />
}
