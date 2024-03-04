import { useState } from 'react';
import { func, number, oneOfType, string } from 'prop-types';
import { Form, Label } from '../semantic_ui_react_wrappers';
import { ReadOnlyOrEditable } from '../context/Permissions';
import { ReadOnlyInput } from './ReadOnlyInput';
import { labelPropType, permissionsPropType } from '../sharedPropTypes';

function EditableIntegerInput(props) {
    let { editableLabel, label, min, prefix, set_value, unit, ...otherProps } = props;
    const initialValue = props.value || 0;
    const [value, setValue] = useState(initialValue)
    const minValue = min || 0;

    function isValid(aValue) {
        if (Number.isNaN(parseInt(aValue))) {
            return false
        }
        if (Number(aValue) < Number(minValue)) {
            return false
        }
        if (props.max !== null && Number(aValue) > Number(props.max)) {
            return false
        }
        return true
    }

    function submitIfChangedAndValid() {
        if (value !== initialValue && isValid(value)) {
            set_value(value)
        }
    }

    return (
        <Form>
            <Form.Input
                {...otherProps}
                error={!isValid(value)}
                fluid
                focus
                label={editableLabel || label}
                labelPosition={unit ? "right" : "left"}
                min={minValue}
                onBlur={() => { submitIfChangedAndValid() }}
                onChange={(event) => { if (isValid(event.target.value)) { setValue(event.target.value) } }}
                onKeyDown={(event) => {
                    if (event.key === "Enter") { submitIfChangedAndValid() }
                    if (event.key === "Escape") { setValue(initialValue) }
                }}
                type="number"
                value={value}
                width={16}
            >
                {prefix ? <Label>{prefix}</Label> : null}
                <input />
                {unit ? <Label>{unit}</Label> : null}
            </Form.Input>
        </Form>
    )
}
EditableIntegerInput.propTypes = {
    editableLabel: labelPropType,
    label: labelPropType,
    max: oneOfType([number, string]),
    min: oneOfType([number, string]),
    prefix: string,
    set_value: func,
    unit: string,
    value: oneOfType([number, string]),
}

export function IntegerInput(props) {
    let { requiredPermissions, ...otherProps } = props;
    return (
        <ReadOnlyOrEditable
            requiredPermissions={requiredPermissions}
            readOnlyComponent={<Form><ReadOnlyInput {...otherProps} /></Form>}
            editableComponent={<EditableIntegerInput {...otherProps} />} />
    )
}
IntegerInput.propTypes = {
    requiredPermissions: permissionsPropType,
}
