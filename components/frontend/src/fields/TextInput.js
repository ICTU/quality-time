import { useState } from "react"
import { bool, func, string } from "prop-types"
import { Form } from "../semantic_ui_react_wrappers"
import { ReadOnlyOrEditable } from "../context/Permissions"
import { labelPropType, permissionsPropType } from "../sharedPropTypes"

function ReadOnlyTextInput({ label, required, value }) {
    return (
        <Form>
            <Form.TextArea
                error={required && value === ""}
                label={label}
                readOnly
                tabIndex={-1}
                value={value}
            />
        </Form>
    )
}
ReadOnlyTextInput.propTypes = {
    label: labelPropType,
    required: bool,
    value: string,
}

function EditableTextInput(props) {
    let { editableLabel, label, required, set_value, ...otherProps } = props
    const initialValue = props.value || ""
    const [text, setText] = useState(initialValue)

    function onKeyDown(event) {
        if (event.key === "Escape") {
            setText(initialValue)
        }
    }
    function onKeyPress(event) {
        if (event.key === "Enter" && event.shiftKey) {
            event.preventDefault()
            submit()
        }
    }
    function submit() {
        if (text !== initialValue) {
            set_value(text)
        }
    }
    return (
        <Form onSubmit={submit}>
            <Form.TextArea
                {...otherProps}
                error={required && text === ""}
                label={editableLabel || label}
                onBlur={submit}
                onChange={(event) => setText(event.target.value)}
                onKeyDown={onKeyDown}
                onKeyPress={onKeyPress}
                value={text}
            />
        </Form>
    )
}
EditableTextInput.propTypes = {
    editableLabel: labelPropType,
    label: labelPropType,
    required: bool,
    set_value: func,
    value: string,
}

export function TextInput(props) {
    let { requiredPermissions, ...otherProps } = props
    return (
        <ReadOnlyOrEditable
            requiredPermissions={requiredPermissions}
            readOnlyComponent={<ReadOnlyTextInput {...otherProps} />}
            editableComponent={<EditableTextInput {...otherProps} />}
        />
    )
}
TextInput.propTypes = {
    requiredPermissions: permissionsPropType,
}
