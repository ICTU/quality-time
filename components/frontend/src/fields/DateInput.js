import { bool, func, string} from 'prop-types';
import { Icon, Label, Form } from '../semantic_ui_react_wrappers';
import { DatePicker } from '../widgets/DatePicker';
import { ReadOnlyOrEditable } from '../context/Permissions';
import { ReadOnlyInput } from './ReadOnlyInput';
import { toISODateStringInCurrentTZ } from '../utils';
import './DateInput.css';
import { labelPropType, permissionsPropType } from '../sharedPropTypes';

function EditableDateInput({ ariaLabelledBy, label, placeholder, required, set_value, value }) {
    value = value ? new Date(value) : null
    return (
        <Form.Input
            aria-labelledby={ariaLabelledBy}
            error={(required && !value)}
            label={label}
            labelPosition="left"
            required={required}
        >
            <Label><Icon fitted name="calendar" /></Label>
            <DatePicker
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
