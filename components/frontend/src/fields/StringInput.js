import React, { useState } from 'react';
import { Form } from '../semantic_ui_react_wrappers';
import { ReadOnlyOrEditable } from '../context/Permissions';
import { Input } from './Input';
import { ReadOnlyInput } from './ReadOnlyInput';

function StringInputWithSuggestions(props) {
    let { editableLabel, label, error, options, required, set_value, warning, ...otherProps } = props;
    const initialValue = props.value || "";
    const [string_options, setOptions] = useState(options);
    const [searchQuery, setSearchQuery] = useState(initialValue);
    return (
        <Form.Dropdown
            {...otherProps}
            allowAdditions
            clearable
            error={error || warning || (required && initialValue === "")}
            fluid
            label={editableLabel || label}
            onAddItem={(_event, { value }) => { setOptions(prev_options => [{ text: value, value: value, key: value }, ...prev_options]) }}
            onChange={(_event, { value }) => { setSearchQuery(value); set_value(value) }}
            onSearchChange={(_event, data) => { setSearchQuery(data.searchQuery) }}
            options={string_options}
            search
            searchQuery={searchQuery}
            selection
        />
    )
}

export function StringInput(props) {
    const { requiredPermissions, options, ...otherProps } = props;
    const optionMap = [...(options || [])].sort().map((value) => ({ key: value, value: value, text: value }));
    const input = <Input {...otherProps} />
    const inputWithSuggestions = <StringInputWithSuggestions options={optionMap} {...otherProps} />;
    return (
        <Form>
            <ReadOnlyOrEditable
                requiredPermissions={requiredPermissions}
                readOnlyComponent={<ReadOnlyInput {...otherProps} />}
                editableComponent={optionMap.length === 0 ? input : inputWithSuggestions} />
        </Form>
    )
}
