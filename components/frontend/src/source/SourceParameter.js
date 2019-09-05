import React from 'react';
import { Icon } from 'semantic-ui-react';
import { StringInput } from '../fields/StringInput';
import { MultipleChoiceInput } from '../fields/MultipleChoiceInput';
import { DateInput } from '../fields/DateInput';
import { IntegerInput } from '../fields/IntegerInput';
import { PasswordInput } from '../fields/PasswordInput';
import { set_source_parameter } from '../api/source';

export function SourceParameter(props) {
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
  const label = props.help_url ?
    <label>{props.parameter_name} <a href={props.help_url}><Icon name="help circle" link /></a></label>
    :
    props.parameter_name;
  if (props.parameter_type === "string") {
    return (
      <StringInput
        label={label}
        options={options()}
        placeholder={props.placeholder}
        readOnly={props.readOnly}
        required={props.required}
        set_value={(value) => set_source_parameter(props.report.report_uuid, props.source_uuid, props.parameter_key, value, props.reload)}
        value={props.parameter_value}
      />
    )
  }
  if (props.parameter_type === "password") {
    return (
      <PasswordInput
        label={label}
        placeholder={props.placeholder}
        readOnly={props.readOnly}
        required={props.required}
        set_value={(value) => set_source_parameter(props.report.report_uuid, props.source_uuid, props.parameter_key, value, props.reload)}
        value={props.parameter_value}
      />
    )
  }
  if (props.parameter_type === "integer") {
    return (
      <IntegerInput
        label={label}
        max={props.parameter_max}
        min={props.parameter_min}
        placeholder={props.placeholder}
        readOnly={props.readOnly}
        required={props.required}
        set_value={(value) => set_source_parameter(props.report.report_uuid, props.source_uuid, props.parameter_key, value, props.reload)}
        value={props.parameter_value}
        unit={props.parameter_unit}
      />
    )
  }
  if (props.parameter_type === "multiple_choice_with_addition") {
    return (
      <MultipleChoiceInput
        allowAdditions
        label={label}
        options={options()}
        placeholder={props.placeholder}
        readOnly={props.readOnly}
        required={props.required}
        set_value={(value) => set_source_parameter(props.report.report_uuid, props.source_uuid, props.parameter_key, value, props.reload)}
        value={props.parameter_value || []}
      />
    )
  }
  if (props.parameter_type === "date") {
    return (
      <DateInput
        label={label}
        readOnly={props.readOnly}
        required={props.required}
        set_value={(value) => set_source_parameter(props.report.report_uuid, props.source_uuid, props.parameter_key, value, props.reload)}
        value={props.parameter_value}
      />
    )
  }
  return (
    <MultipleChoiceInput
      label={label}
      options={props.parameter_values}
      placeholder={props.placeholder}
      readOnly={props.readOnly}
      required={props.required}
      set_value={(value) => set_source_parameter(props.report.report_uuid, props.source_uuid, props.parameter_key, value, props.reload)}
      value={props.parameter_value || []}
    />
  )
}
