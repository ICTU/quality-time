import React from 'react';
import { Icon } from 'semantic-ui-react';
import { StringInput } from '../fields/StringInput';
import { MultipleChoiceInput } from '../fields/MultipleChoiceInput';
import { DateInput } from '../fields/DateInput';
import { IntegerInput } from '../fields/IntegerInput';
import { PasswordInput } from '../fields/PasswordInput';
import { set_source_parameter } from '../api/source';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';

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
    <label>{props.parameter_name} <a href={props.help_url} target="_blank" title="Opens new window or tab" rel="noopener noreferrer"><Icon name="help circle" link /></a></label>
    :
    props.parameter_name;
  const parameter_props = {label: label, placeholder: props.placeholder, required: props.required};
  if (props.parameter_type === "url") {
    return (
      <StringInput
        {...parameter_props}
        options={options()}
        set_value={(value) => set_source_parameter(props.report.report_uuid, props.source_uuid, props.parameter_key, value, props.reload)}
        value={props.parameter_value}
        warning={props.warning}
      />
    )
  }
  else if (props.parameter_type === "string") {
    return (
      <StringInput
        {...parameter_props}
        options={options()}
        set_value={(value) => set_source_parameter(props.report.report_uuid, props.source_uuid, props.parameter_key, value, props.reload)}
        value={props.parameter_value}
      />
    )
  }
  else if (props.parameter_type === "password") {
    return (
      <PasswordInput
        {...parameter_props}
        set_value={(value) => set_source_parameter(props.report.report_uuid, props.source_uuid, props.parameter_key, value, props.reload)}
        value={props.parameter_value}
      />
    )
  }
  else if (props.parameter_type === "integer") {
    return (
      <IntegerInput
        {...parameter_props}
        max={props.parameter_max}
        min={props.parameter_min}
        set_value={(value) => set_source_parameter(props.report.report_uuid, props.source_uuid, props.parameter_key, value, props.reload)}
        value={props.parameter_value}
        unit={props.parameter_unit}
      />
    )
  }
  else if (props.parameter_type === "multiple_choice_with_addition") {
    return (
      <MultipleChoiceInput
        {...parameter_props}
        allowAdditions
        options={options()}
        set_value={(value) => set_source_parameter(props.report.report_uuid, props.source_uuid, props.parameter_key, value, props.reload)}
        value={props.parameter_value || []}
      />
    )
  }
  else if (props.parameter_type === "date") {
    return (
      <DateInput
        {...parameter_props}
        set_value={(value) => set_source_parameter(props.report.report_uuid, props.source_uuid, props.parameter_key, value, props.reload)}
        value={props.parameter_value}
      />
    )
  }
  if (props.parameter_type === "single_choice") {
    return (
      <SingleChoiceInput
        {...parameter_props}
        options={props.parameter_values.map(value => ({key: value, text: value, value: value}))}
        set_value={(value) => set_source_parameter(props.report.report_uuid, props.source_uuid, props.parameter_key, value, props.reload)}
        value={props.parameter_value}
      />
    )
  }
  return (
    <MultipleChoiceInput
      {...parameter_props}
      options={props.parameter_values}
      set_value={(value) => set_source_parameter(props.report.report_uuid, props.source_uuid, props.parameter_key, value, props.reload)}
      value={props.parameter_value || []}
    />
  )
}
