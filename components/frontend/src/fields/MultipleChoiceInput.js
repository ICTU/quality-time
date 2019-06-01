import React, { useEffect, useState } from 'react';
import { Form } from 'semantic-ui-react';

function sort_options(option_list) {
  let options = new Set();
  option_list.forEach((option) => { options.add({ key: option, text: option, value: option }) });
  options = Array.from(options);
  options.sort((a, b) => a.text.localeCompare(b.text));
  return options;
}

export function MultipleChoiceInput(props) {
  let { required, set_value, allowAdditions, ...otherProps } = props;
  const [value, setValue] = useState(props.value || []);
  useEffect(() => { props.set_value(value) }, [value]);
  const [options, setOptions] = useState(sort_options(props.options));
  return (
    <Form>
      {props.readOnly ?
        <Form.Input
          {...otherProps}
        />
        :
        <Form.Dropdown
          {...otherProps}
          allowAdditions={allowAdditions}
          error={required && value.length === 0}
          fluid
          multiple
          onAddItem={(event, { value }) => { setOptions(options => sort_options([value, ...options.map(option => option.text)])) }}
          onChange={(event, { value }) => { setValue(value) }}
          options={options}
          search
          selection
          value={value}
        />
      }
    </Form>
  )
}
