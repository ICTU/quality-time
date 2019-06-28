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
  let { allowAdditions, required, set_value, ...otherProps } = props;
  const [value, setValue] = useState(props.value || []);
  useEffect(() => { const new_value = props.value || []; if (new_value !== value) { setValue(new_value) } }, [props.value]);
  const [options, setOptions] = useState(props.options);
  useEffect(() => { const new_options = props.options; if (new_options !== options) { setOptions(new_options) } }, [props.options]);
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
          onAddItem={(event, { added_value }) => { setOptions(prev_options => ([added_value, ...prev_options])) }}
          onChange={(event, { new_value }) => { setValue(new_value); if (new_value !== props.value) { set_value(new_value) } }}
          options={sort_options(options)}
          search
          selection
          value={value}
        />
      }
    </Form>
  )
}
