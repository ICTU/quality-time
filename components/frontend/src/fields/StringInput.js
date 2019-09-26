import React, { useEffect, useState } from 'react';
import { Form } from 'semantic-ui-react';
import { Input } from './Input';

function StringInputWithSuggestions(props) {
  // console.log("1>>", props)
  let { required, options, set_value, value, ...otherProps } = props;
  // console.log("1>required>", required)
  // console.log("1>options>", options)
  // console.log("1>set_value>", set_value)
  // console.log("1>value>", value)
  // console.log("1>otherProps>", otherProps)
  const [string_options, setOptions] = useState(options);
  // console.log("2>>", string_options)
  // console.log("3>>", setOptions)
  useEffect(() => setOptions(props.options), [props.options]);
  const [search_query, setSearchQuery] = useState(value || '');
  // console.log("4>>", search_query)
  // console.log("5>>", setSearchQuery)
  useEffect(() => setSearchQuery(props.value || ''), [props.value]);
  return (
    <Form>
      <Form.Dropdown
        {...otherProps}
        allowAdditions
        error={required && search_query === ""}
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
