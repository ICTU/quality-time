import { useState } from 'react';
import { bool, func, number, oneOfType, string } from 'prop-types';
import { StringInput } from '../fields/StringInput';
import { MultipleChoiceInput } from '../fields/MultipleChoiceInput';
import { DateInput } from '../fields/DateInput';
import { IntegerInput } from '../fields/IntegerInput';
import { PasswordInput } from '../fields/PasswordInput';
import { set_source_parameter } from '../api/source';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { LabelWithDropdown } from '../widgets/LabelWithDropdown';
import { LabelWithHelp } from '../widgets/LabelWithHelp';
import { LabelWithHyperLink } from '../widgets/LabelWithHyperLink';
import { LabelDate } from '../widgets/LabelWithDate';
import { dropdownOptions } from '../utils';
import { labelPropType, permissionsPropType, popupContentPropType, reportPropType, sourcePropType, stringsPropType } from '../sharedPropTypes';

function SourceParameterLabel({
    edit_scope,
    index,
    label,
    parameter_short_name,
    setEditScope,
    source_type_name,
}) {
    const scope_options = [
        { key: "source", value: "source", text: "Apply change to source", description: `Change the ${parameter_short_name} of this ${source_type_name} source only`, label: { color: 'grey', empty: true, circular: true } },
        { key: "metric", value: "metric", text: "Apply change to metric", description: `Change the ${parameter_short_name} of ${source_type_name} sources in this metric that have the same ${parameter_short_name}`, label: { color: 'black', empty: true, circular: true } },
        { key: "subject", value: "subject", text: "Apply change to subject", description: `Change the ${parameter_short_name} of ${source_type_name} sources in this subject that have the same ${parameter_short_name}`, label: { color: 'yellow', empty: true, circular: true } },
        { key: "report", value: "report", text: "Apply change to report", description: `Change the ${parameter_short_name} of ${source_type_name} sources in this report that have the same ${parameter_short_name}`, label: { color: 'orange', empty: true, circular: true } },
        { key: "reports", value: "reports", text: "Apply change to all reports", description: `Change the ${parameter_short_name} of ${source_type_name} sources in all reports that have the same ${parameter_short_name}`, label: { color: 'red', empty: true, circular: true } }];
    return (
        <LabelWithDropdown
            color={{ source: "grey", metric: "black", subject: "gold", report: "orange", reports: "red" }[edit_scope]}
            direction={index % 2 === 0 ? "right" : "left"}
            label={label}
            onChange={(_event, data) => setEditScope(data.value)}
            options={scope_options}
            value={edit_scope} />
    )
}
SourceParameterLabel.propTypes = {
    edit_scope: string,
    index: number,
    label: labelPropType,
    parameter_short_name: string,
    setEditScope: func,
    source_type_name: string,
}

export function SourceParameter({
    help,
    help_url,
    index,
    parameter_key,
    parameter_type,
    parameter_name,
    parameter_short_name,
    parameter_unit,
    parameter_min,
    parameter_max,
    parameter_value,
    parameter_values,
    placeholder,
    reload,
    report,
    required,
    requiredPermissions,
    source,
    source_type_name,
    source_uuid,
    warning,
}) {
    const [edit_scope, setEditScope] = useState("source");
    function options() {
        let values = new Set();
        // Collect all values in the current report used for this parameter, for this source type:
        Object.values(report.subjects).forEach((subject) => {
            Object.values(subject.metrics).forEach((metric) => {
                Object.values(metric.sources).forEach((metric_source) => {
                    if (metric_source.type === source.type && metric_source.parameters) {
                        const value = metric_source.parameters[parameter_key];
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
        return Array.from(values);
    }
    let label = parameter_name;
    if (help_url) {
        label = <LabelWithHyperLink label={parameter_name} url={help_url} />
    }
    if (help) {
        label = <LabelWithHelp label={parameter_name} help={help} />
    }
    if (parameter_type === "date") {
        const date = new Date(Date.parse(parameter_value))
        label = <span>{label}<LabelDate date={date} /></span>
    }
    let parameter_props = {
        requiredPermissions: requiredPermissions,
        editableLabel: <SourceParameterLabel
            edit_scope={edit_scope}
            label={label}
            setEditScope={setEditScope}
            source_type_name={source_type_name}
            parameter_short_name={parameter_short_name}
            index={index} />,
        label: label,
        placeholder: placeholder,
        required: required,
        set_value: ((value) => {
            set_source_parameter(source_uuid, parameter_key, value, edit_scope, reload)
            setEditScope("source")  // Reset the edit scope of the parameter to source only
        }),
        value: parameter_value
    };
    if (parameter_type === "date") {
        return (<DateInput {...parameter_props} />)
    }
    if (parameter_type === "password") {
        return (<PasswordInput {...parameter_props} />)
    }
    if (parameter_type === "integer") {
        return (<IntegerInput {...parameter_props} max={parameter_max} min={parameter_min} unit={parameter_unit} />)
    }
    if (parameter_type === "single_choice") {
        return (<SingleChoiceInput {...parameter_props} options={dropdownOptions(parameter_values)} />)
    }
    if (parameter_type === "multiple_choice") {
        return (<MultipleChoiceInput {...parameter_props} options={dropdownOptions(parameter_values)} />)
    }
    if (parameter_type === "multiple_choice_with_addition") {
        return (<MultipleChoiceInput {...parameter_props} options={dropdownOptions(parameter_values)} allowAdditions />)
    }
    parameter_props["options"] = options();
    if (parameter_type === "string") {
        return (<StringInput {...parameter_props} />)
    }
    if (parameter_type === "url") {
        return (<StringInput {...parameter_props} error={warning} />)
    }
    return null;
}
SourceParameter.propTypes = {
    help: popupContentPropType,
    help_url: string,
    index: number,
    parameter_key: string,
    parameter_type: string,
    parameter_name: string,
    parameter_short_name: string,
    parameter_unit: string,
    parameter_min: number,
    parameter_max: number,
    parameter_value: oneOfType([string, stringsPropType]),
    parameter_values: stringsPropType,
    placeholder: string,
    reload: func,
    report: reportPropType,
    required: bool,
    requiredPermissions: permissionsPropType,
    source: sourcePropType,
    source_type_name: string,
    source_uuid: string,
    warning: bool,
}
