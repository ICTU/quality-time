import React, { useState } from 'react';
import { Form } from '../semantic_ui_react_wrappers';
import { ReadOnlyOrEditable } from '../context/Permissions';
import { ReadOnlyInput } from './ReadOnlyInput';

function assembleOptions(optionList, values) {
    // Create a sorted list of unique options. Also include the current values, or they won't be displayed or some reason
    let options = new Set();
    (optionList || []).forEach((option) => { options.add(option) });
    (values || []).forEach((value) => { options.add({ key: value, text: value, value: value }) })
    options = Array.from(options);
    options.sort((a, b) => a.text.localeCompare(b.text));
    return options;
}

export function MultipleChoiceInput(props) {
    let { allowAdditions, editableLabel, onSearchChange, required, set_value, requiredPermissions, ...otherProps } = props;
    const [values, setValues] = useState(props.value || [])
    const [searchQuery, setSearchQuery] = useState("");
    return (
        <Form>
            <ReadOnlyOrEditable
                requiredPermissions={requiredPermissions}
                readOnlyComponent={<ReadOnlyInput {...otherProps} value={values.join(", ")} />}
                editableComponent={
                    <Form.Dropdown
                        {...otherProps}
                        allowAdditions={allowAdditions}
                        error={required && values.length === 0}
                        fluid
                        label={editableLabel || props.label}
                        multiple
                        onAddItem={() => setSearchQuery("")}
                        onBlur={() => {
                            if (searchQuery && !values.includes(searchQuery)) {
                                // Save the data on loss of focus like we do with other input types
                                let newValues = values.concat(searchQuery);
                                setValues(newValues);
                                set_value(newValues)
                            }
                            setSearchQuery("");
                        }}
                        onChange={(_event, data) => {
                            setValues(data.value);
                            set_value(data.value);
                            setSearchQuery("");
                        }}
                        onSearchChange={(event, data) => {
                            event.preventDefault();
                            setSearchQuery(data.searchQuery)
                            if (onSearchChange) { onSearchChange(data.searchQuery) }
                        }}
                        options={assembleOptions(props.options, values)}
                        search
                        searchQuery={searchQuery}
                        selection
                        value={values}
                    />
                }
            />
        </Form>
    )
}
