import "./Form.css"

import { useContext } from "react"
import { Form as SemanticUIForm } from "semantic-ui-react"

import { DarkMode } from "../context/DarkMode"

export function Form(props) {
    return <SemanticUIForm inverted={useContext(DarkMode)} {...props} />
}

function Input(props) {
    return <SemanticUIForm.Input inverted={useContext(DarkMode)} {...props} />
}

function Dropdown(props) {
    return <SemanticUIForm.Dropdown inverted={useContext(DarkMode) ? "true" : undefined} {...props} />
}

Form.Button = SemanticUIForm.Button
Form.Dropdown = Dropdown
Form.Input = Input
Form.TextArea = SemanticUIForm.TextArea
