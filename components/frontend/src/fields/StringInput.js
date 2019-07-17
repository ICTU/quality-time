import React, { useEffect, useState } from 'react';
import { Form } from 'semantic-ui-react';
import { Input } from './Input';

function StringInputWithSuggestions(props) {
  let { required, options, set_value, value, ...otherProps } = props;
  const [string_value, setValue] = useState(value || '');
  useEffect(() => setValue(props.value || ''), [props.value]);
  const [string_options, setOptions] = useState(options);
  useEffect(() => setOptions(props.options), [props.options]);
  return (
    <Form>
      <Form.Dropdown
        {...otherProps}
        allowAdditions
        error={required && string_value === ""}
        fluid
        onAddItem={(event, { value }) => setOptions(prev_options => [{ text: value, value: value, key: value }, ...prev_options])}
        onChange={(event, { value }) => { setValue(value); if (value !== props.value) { set_value(value) } }}
        options={string_options}
        search
        selection
        value={string_value}
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
