import { array, bool, func, string } from "prop-types"
import { useState } from "react"

import { ReadOnlyOrEditable } from "../context/Permissions"
import { Form } from "../semantic_ui_react_wrappers"
import { labelPropType, permissionsPropType, stringsPropType } from "../sharedPropTypes"
import { sortWithLocaleCompare } from "../utils"
import { Input } from "./Input"
import { ReadOnlyInput } from "./ReadOnlyInput"

function StringInputWithSuggestions(props) {
    let { editableLabel, label, error, options, placeholder, required, set_value, warning, ...otherProps } = props
    placeholder = placeholder || "none"
    const initialValue = props.value || ""
    const [stringOptions, setStringOptions] = useState([
        ...options,
        { text: <font color="lightgrey">{placeholder}</font>, value: "", key: "" },
    ])
    const [searchQuery, setSearchQuery] = useState(initialValue)
    return (
        <Form.Dropdown
            {...otherProps}
            allowAdditions
            clearable
            error={error || warning || (required && initialValue === "")}
            fluid
            label={editableLabel || label}
            onAddItem={(_event, { value }) => {
                setStringOptions((prev_options) => [{ text: value, value: value, key: value }, ...prev_options])
            }}
            onChange={(_event, { value }) => {
                setSearchQuery(value)
                set_value(value)
            }}
            onSearchChange={(_event, data) => {
                setSearchQuery(data.searchQuery)
            }}
            options={stringOptions}
            placeholder={placeholder}
            search
            searchQuery={searchQuery}
            selection
        />
    )
}
StringInputWithSuggestions.propTypes = {
    editableLabel: labelPropType,
    label: labelPropType,
    error: bool,
    options: array,
    placeholder: string,
    required: bool,
    set_value: func,
    value: string,
    warning: bool,
}

export function StringInput(props) {
    const { requiredPermissions, options, ...otherProps } = props
    const optionsArray = [...(options || [])]
    sortWithLocaleCompare(optionsArray)
    const optionMap = optionsArray.map((value) => ({ key: value, value: value, text: value }))
    const input = <Input {...otherProps} />
    const inputWithSuggestions = <StringInputWithSuggestions options={optionMap} {...otherProps} />
    return (
        <Form>
            <ReadOnlyOrEditable
                requiredPermissions={requiredPermissions}
                readOnlyComponent={<ReadOnlyInput {...otherProps} />}
                editableComponent={optionMap.length === 0 ? input : inputWithSuggestions}
            />
        </Form>
    )
}
StringInput.propTypes = {
    requiredPermissions: permissionsPropType,
    options: stringsPropType,
}
