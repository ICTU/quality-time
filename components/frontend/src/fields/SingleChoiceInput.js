import React, { useEffect, useState } from 'react';
import { Form } from 'semantic-ui-react';
import { ReadOnlyOrEditable } from '../context/ReadOnly';

export function SingleChoiceInput(props) {
  const value_text = props.options.filter(({ value }) => value === props.value)[0].text;
  let { set_value, options, ...otherProps } = props;
  options.sort((a, b) => a.text.localeCompare(b.text));
  const [choice, setChoice] = useState(props.value);
  useEffect(() => setChoice(props.value), [props.value]);
  return (
    <Form>
      <ReadOnlyOrEditable
        readOnlyComponent={<Form.Input {...otherProps} value={value_text} />}
        editableComponent={
          <Form.Dropdown
            {...otherProps}
            fluid
            onChange={(event, { name, value }) => { setChoice(value); if (value !== props.value) { set_value(value) } }}
            options={options}
            search
            selection
            selectOnNavigation={false}
            tabIndex="0"
            value={choice}
          />
        }
      />
    </Form>
    )
  }
