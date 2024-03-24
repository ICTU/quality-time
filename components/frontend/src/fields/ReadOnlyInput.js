import { bool, number, oneOfType, string } from "prop-types"

import { Form, Label } from "../semantic_ui_react_wrappers"
import { labelPropType } from "../sharedPropTypes"

export function ReadOnlyInput({ error, label, placeholder, prefix, required, value, type, unit }) {
    return (
        <Form.Input
            error={error || (required && value === "")}
            fluid
            label={label}
            labelPosition={unit ? "right" : "left"}
            placeholder={placeholder}
            readOnly
            tabIndex={-1}
            type={type}
            value={value || ""}
        >
            {prefix ? <Label>{prefix}</Label> : null}
            <input />
            {unit ? <Label>{unit}</Label> : null}
        </Form.Input>
    )
}
ReadOnlyInput.propTypes = {
    error: bool,
    label: labelPropType,
    placeholder: string,
    prefix: string,
    required: bool,
    value: oneOfType([bool, number, string]),
    type: string,
    unit: string,
}
