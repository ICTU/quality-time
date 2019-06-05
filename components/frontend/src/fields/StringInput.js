import React, { useEffect, useState } from 'react';
import { Form } from 'semantic-ui-react';
import { Input } from './Input';

function StringInputWithSuggestions(props) {
  let { required, options, set_value, value, ...otherProps } = props;
  const [string_value, setValue] = useState(value || '');
  useEffect(() => { const new_value = props.value || ''; if (new_value !== string_value) { setValue(new_value) } }, [props.value]);
  const [string_options, setOptions] = useState(options);
  useEffect(() => { const new_options = props.options; if (new_options !== string_options) { setOptions(new_options) } }, [props.options]);
  return (
    <Form>
      <Form.Dropdown
        {...otherProps}
        allowAdditions
        error={required && string_value === ""}
        fluid
        onAddItem={(event, { value }) => setOptions(options => [{ text: value, value: value, key: value }, ...options])}
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
  const options = props.options || [];
  return props.readOnly || options.length === 0 ?
    <Input {...props} />
    :
    <StringInputWithSuggestions {...props} />
}
