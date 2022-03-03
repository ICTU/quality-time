import React, { useContext } from 'react';
import { Form as SemanticUIForm } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';
import './Form.css';

export function Form(props) {
    return (
        <SemanticUIForm inverted={useContext(DarkMode)} {...props} />
    )
}

function Input(props) {
    return (
        <SemanticUIForm.Input inverted={useContext(DarkMode)} {...props} />
    )
}

Form.Button = SemanticUIForm.Button
Form.Dropdown = SemanticUIForm.Dropdown
Form.Input = Input
Form.TextArea = SemanticUIForm.TextArea
