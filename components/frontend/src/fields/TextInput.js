import React, { useState } from 'react';
import { Form } from 'semantic-ui-react';
import { ReadOnlyOrEditable } from '../context/Permissions';

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

function EditableTextInput(props) {
    let { editableLabel, label, required, set_value, ...otherProps } = props;
    const [text, setText] = useState(props.value || '');
    function onChange(event) {
        setText(event.target.value)
    }
    function onKeyDown(event) {
        if (event.key === "Escape") {
            setText(props.value || '')
        }
    }
    function onKeyPress(event) {
        if (event.key === "Enter" && event.shiftKey && text !== (props.value || '')) {
            event.preventDefault();
            props.set_value(text);
        }
    }
    function submit() {
        if (text !== (props.value || '')) {
            props.set_value(text)
        }
    }
    return (
        <Form onSubmit={submit}>
            <Form.TextArea
                {...otherProps}
                error={required && text === ""}
                label={editableLabel || label}
                onBlur={submit}
                onChange={onChange}
                onKeyDown={onKeyDown}
                onKeyPress={onKeyPress}
                value={text}
            />
        </Form>
    )
}

export function TextInput(props) {
    let { requiredPermissions, ...otherProps } = props;
    return (
        <ReadOnlyOrEditable
            requiredPermissions={requiredPermissions}
            readOnlyComponent={<ReadOnlyTextInput {...otherProps} />}
            editableComponent={<EditableTextInput {...otherProps} />} />
    )
}
