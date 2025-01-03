import "./DateInput.css"

import { bool, func, string } from "prop-types"

import { ReadOnlyOrEditable } from "../context/Permissions"
import { Form, Label } from "../semantic_ui_react_wrappers"
import { labelPropType, permissionsPropType } from "../sharedPropTypes"
import { toISODateStringInCurrentTZ } from "../utils"
import { DatePicker } from "../widgets/DatePicker"
import { CalendarIcon } from "../widgets/icons"
import { ReadOnlyInput } from "./ReadOnlyInput"

function EditableDateInput({ ariaLabelledBy, label, placeholder, required, set_value, value }) {
    value = value ? new Date(value) : null
    return (
        <Form.Input error={required && !value} label={label} labelPosition="left" required={required}>
            <Label style={{ padding: "8px" }}>
                <CalendarIcon />
            </Label>
            <DatePicker
                ariaLabelledBy={ariaLabelledBy}
                selected={value}
                isClearable={!required}
                onChange={(newDate) => {
                    let dateValue = null
                    if (newDate !== null) {
                        dateValue = toISODateStringInCurrentTZ(newDate)
                    }
                    set_value(dateValue)
                }}
                placeholderText={placeholder}
            />
        </Form.Input>
    )
}
EditableDateInput.propTypes = {
    ariaLabelledBy: string,
    label: labelPropType,
    placeholder: string,
    required: bool,
    set_value: func,
    value: string,
}

export function DateInput(props) {
    return (
        <Form>
            <ReadOnlyOrEditable
                requiredPermissions={props.requiredPermissions}
                readOnlyComponent={<ReadOnlyInput {...props} />}
                editableComponent={<EditableDateInput {...props} label={props.editableLabel || props.label} />}
            />
        </Form>
    )
}
DateInput.propTypes = {
    editableLabel: labelPropType,
    label: labelPropType,
    requiredPermissions: permissionsPropType,
}
