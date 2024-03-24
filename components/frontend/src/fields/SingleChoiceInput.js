import { Form } from "../semantic_ui_react_wrappers"
import { array, bool, func, number, oneOfType, string } from "prop-types"
import { ReadOnlyOrEditable } from "../context/Permissions"
import { ReadOnlyInput } from "./ReadOnlyInput"
import { labelPropType, permissionsPropType } from "../sharedPropTypes"

function SingleChoiceDropdown(props) {
    let { editableLabel, options, setValue, ...otherProps } = props
    return (
        <Form.Dropdown
            {...otherProps}
            fluid
            label={editableLabel || props.label}
            onChange={(_event, { value }) => {
                setValue(value)
            }}
            options={options}
            search
            selection
            selectOnNavigation={false}
            tabIndex="0"
            value={props.value}
        />
    )
}
SingleChoiceDropdown.propTypes = {
    editableLabel: labelPropType,
    label: labelPropType,
    options: array,
    setValue: func,
    value: oneOfType([bool, number, string]),
}

export function SingleChoiceInput(props) {
    const option_value = props.options.filter(({ value }) => value === props.value)[0]
    const value_text = option_value ? option_value.text : ""
    let { editableLabel, set_value, options, sort, requiredPermissions, ...otherProps } = props

    // default should be sorted
    if (sort || sort === undefined) {
        options.sort((a, b) => a.text.localeCompare(b.text))
    }

    return (
        <Form>
            <ReadOnlyOrEditable
                requiredPermissions={requiredPermissions}
                readOnlyComponent={<ReadOnlyInput {...otherProps} value={value_text} />}
                editableComponent={
                    <SingleChoiceDropdown
                        editableLabel={editableLabel}
                        options={options}
                        setValue={set_value}
                        {...otherProps}
                    />
                }
            />
        </Form>
    )
}
SingleChoiceInput.propTypes = {
    editableLabel: labelPropType,
    label: labelPropType,
    options: array,
    requiredPermissions: permissionsPropType,
    set_value: func,
    sort: bool,
    value: oneOfType([bool, number, string]),
}
