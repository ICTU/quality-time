import React, { useState } from 'react';
import { Form } from '../semantic_ui_react_wrappers';
import { ReadOnlyOrEditable } from '../context/Permissions';
import { ReadOnlyInput } from './ReadOnlyInput';

function sort_options(option_list) {
    let options = new Set();
    option_list.forEach((option) => { options.add({ key: option, text: option, value: option }) });
    options = Array.from(options);
    options.sort((a, b) => a.text.localeCompare(b.text));
    return options;
}

export function MultipleChoiceInput(props) {
    let { allowAdditions, editableLabel, required, set_value, requiredPermissions, ...otherProps } = props;
    const [value, setValue] = useState(props.value || [])
    const [options, setOptions] = useState(props.options);
    const [searchQuery, setSearchQuery] = useState("");
    return (
        <Form>
            <ReadOnlyOrEditable
                requiredPermissions={requiredPermissions}
                readOnlyComponent={<ReadOnlyInput {...otherProps} value={value ? value.join(", ") : ''}  />}
                editableComponent={
                    <Form.Dropdown
                        {...otherProps}
                        allowAdditions={allowAdditions}
                        error={required && value.length === 0}
                        fluid
                        label={editableLabel || props.label}
                        multiple
                        onAddItem={(event, { value: addedValue }) => {
                            if (!options.includes(addedValue)) {
                                setOptions(prevOptions => ([addedValue, ...prevOptions]))
                            }
                            setSearchQuery("");
                        }}
                        onBlur={() => {
                            if (searchQuery && !value.includes(searchQuery)) {
                                // Save the data on loss of focus like we do with other input types
                                let newValue = value.concat(searchQuery);
                                setOptions(prevOptions => ([searchQuery, ...prevOptions]))
                                setValue(newValue);
                                set_value(newValue)
                            }
                            setSearchQuery("");
                        }}
                        onChange={(event, { value: changedValue }) => {
                            setValue(changedValue);
                            set_value(changedValue)
                            setSearchQuery("");
                        }}
                        onSearchChange={(event, data) => {
                            event.preventDefault();
                            setSearchQuery(data.searchQuery)
                        }}
                        options={sort_options(options)}
                        search
                        searchQuery={searchQuery}
                        selection
                        value={value}
                    />
                }
            />
        </Form>
    )
}
