import React, { useState } from 'react';
import { Icon, Popup } from 'semantic-ui-react';
import { StringInput } from '../fields/StringInput';
import { MultipleChoiceInput } from '../fields/MultipleChoiceInput';
import { DateInput } from '../fields/DateInput';
import { IntegerInput } from '../fields/IntegerInput';
import { PasswordInput } from '../fields/PasswordInput';
import { set_source_parameter } from '../api/source';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { LabelWithDropdown } from '../widgets/LabelWithDropdown';
import { HyperLink } from '../widgets/HyperLink';

function SourceParameterLabel(props) {
    const scope_options = [
        { key: "source", value: "source", text: "source", description: `Change this ${props.source_type_name} only`, label: { color: 'grey', empty: true, circular: true } },
        { key: "metric", value: "metric", text: "metric", description: `Change each ${props.source_type_name} of this metric that has the same ${props.parameter_short_name}`, label: { color: 'black', empty: true, circular: true } },
        { key: "subject", value: "subject", text: "subject", description: `Change each ${props.source_type_name} in this subject that has the same ${props.parameter_short_name}`, label: { color: 'yellow', empty: true, circular: true } },
        { key: "report", value: "report", text: "report", description: `Change each ${props.source_type_name} in this report that has the same ${props.parameter_short_name}`, label: { color: 'orange', empty: true, circular: true } },
        { key: "reports", value: "reports", text: "all reports", description: `Change each ${props.source_type_name} in each report that has the same ${props.parameter_short_name}`, label: { color: 'red', empty: true, circular: true } }];
    return (
        <LabelWithDropdown
            color={{ source: "grey", metric: "black", subject: "gold", report: "orange", reports: "red" }[props.edit_scope]}
            direction={props.index % 2 === 0 ? "right" : "left"} label={props.label} onChange={(event, data) => props.setEditScope(data.value)} options={scope_options} prefix="Apply change to"
            value={props.edit_scope} />
    )
}

export function SourceParameter(props) {
    const [edit_scope, setEditScope] = useState("source");
    function options() {
        let values = new Set();
        // Collect all values in the current report used for this parameter, for this source type:
        Object.values(props.report.subjects).forEach((subject) => {
            Object.values(subject.metrics).forEach((metric) => {
                Object.values(metric.sources).forEach((source) => {
                    if (source.type === props.source.type && source.parameters) {
                        const value = source.parameters[props.parameter_key];
                        if (value) {
                            if (Array.isArray(value)) {
                                value.forEach((item) => values.add(item))
                            } else {
                                values.add(value)
                            }
                        }
                    }
                })
            })
        });
        return values;
    }
    var label = props.parameter_name;
    if (props.help_url) {
        label = <label>{props.parameter_name} <HyperLink url={props.help_url}><Icon name="help circle" link /></HyperLink></label>
    }
    if (props.help) {
        label = <label>{props.parameter_name} <Popup on={['hover', 'focus']} content={props.help} trigger={<Icon tabIndex="0" name="help circle" />} /></label>
    }
    let parameter_props = {
        requiredPermissions: props.requiredPermissions,
        editableLabel: <SourceParameterLabel edit_scope={edit_scope} label={label} setEditScope={setEditScope} {...props} />,
        label: label,
        placeholder: props.placeholder,
        required: props.required,
        set_value: ((value) => set_source_parameter(props.source_uuid, props.parameter_key, value, edit_scope, props.reload)),
        value: props.parameter_value
    };
    if (props.parameter_type === "date") {
        return (<DateInput {...parameter_props} />)
    }
    if (props.parameter_type === "password") {
        return (<PasswordInput {...parameter_props} />)
    }
    if (props.parameter_type === "integer") {
        return (<IntegerInput {...parameter_props} max={props.parameter_max} min={props.parameter_min} unit={props.parameter_unit} />)
    }
    if (props.parameter_type === "single_choice") {
        return (<SingleChoiceInput {...parameter_props} options={props.parameter_values.map(value => ({ key: value, text: value, value: value }))} />)
    }
    if (props.parameter_type === "multiple_choice") {
        return (<MultipleChoiceInput {...parameter_props} options={props.parameter_values} />)
    }
    parameter_props["options"] = options();
    if (props.parameter_type === "string") {
        return (<StringInput {...parameter_props} />)
    }
    if (props.parameter_type === "url") {
        return (<StringInput {...parameter_props} warning={props.warning} />)
    }
    if (props.parameter_type === "multiple_choice_with_addition") {
        return (<MultipleChoiceInput {...parameter_props} allowAdditions />)
    }
    return null;
}
