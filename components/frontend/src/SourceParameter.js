import React, { Component } from 'react';
import { Icon } from 'semantic-ui-react';
import { StringInput } from './fields/StringInput';
import { MultipleChoiceInput } from './fields/MultipleChoiceInput';
import { DateInput } from './fields/DateInput';
import { IntegerInput } from './fields/IntegerInput';
import { Input } from './fields/Input';

class SourceParameter extends Component {
  constructor(props) {
    super(props);
    this.state = { options: this.options() }
  }
  componentDidUpdate(prevProps) {
    if (prevProps.source.type !== this.props.source.type) {
      this.setState({ options: this.options() })
    }
  }
  options() {
    let values = new Set();
    if (this.props.parameter_type === "string") {
      // Collect all values in the current report used for this parameter, for this source type:
      Object.values(this.props.report.subjects).forEach((subject) => {
        Object.values(subject.metrics).forEach((metric) => {
          Object.values(metric.sources).forEach((source) => {
            if (source.type === this.props.source.type && source.parameters) {
              const value = source.parameters[this.props.parameter_key];
              if (value) {
                values.add(value);
              }
            }
          })
        })
      });
    }
    return [...values].sort().map((value) => ({ key: value, value: value, text: value }));
  }
  set_source_parameter(key, value) {
    let self = this;
    fetch(`${window.server_url}/report/${this.props.report.report_uuid}/source/${this.props.source_uuid}/parameter/${key}`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ [key]: value })
    })
      .then(function (response) {
        return response.json();
      })
      .then(function (json) {
        self.props.reload();
      })
      .catch(function (error) {
        console.log(error);
      })
  }
  render() {
    const label = this.props.help_url ?
      <label>{this.props.parameter_name} <a href={this.props.help_url}><Icon name="help circle" link /></a></label>
      :
      this.props.parameter_name;
    if (this.props.parameter_type === "string") {
      return (
        <StringInput
          label={label}
          options={this.state.options}
          placeholder={this.props.placeholder}
          readOnly={this.props.readOnly}
          required={this.props.required}
          set_value={(value) => this.set_source_parameter(this.props.parameter_key, value)}
          value={this.props.parameter_value}
        />
      )
    };
    if (this.props.parameter_type === "password") {
      return (
        <Input
          label={label}
          placeholder={this.props.placeholder}
          readOnly={this.props.readOnly}
          required={this.props.required}
          set_value={(value) => this.set_source_parameter(this.props.parameter_key, value)}
          type="password"
          value={this.props.parameter_value}
        />
      )
    }
    if (this.props.parameter_type === "integer") {
      return (
        <IntegerInput
          label={label}
          placeholder={this.props.placeholder}
          readOnly={this.props.readOnly}
          required={this.props.required}
          set_value={(value) => this.set_source_parameter(this.props.parameter_key, value)}
          value={this.props.parameter_value}
          unit={this.props.parameter_unit}
        />
      )
    }
    if (this.props.parameter_type === "multiple_choice_with_addition") {
      return (
        <MultipleChoiceInput
          allowAdditions
          label={label}
          options={this.props.parameter_values}
          placeholder={this.props.placeholder}
          readOnly={this.props.readOnly}
          required={this.props.required}
          set_value={(value) => this.set_source_parameter(this.props.parameter_key, value)}
          value={this.props.parameter_value || []}
        />
      )
    }
    if (this.props.parameter_type === "date") {
      return (
        <DateInput
          label={label}
          readOnly={this.props.readOnly}
          required={this.props.required}
          set_value={(value) => this.set_source_parameter(this.props.parameter_key, value)}
          value={this.props.parameter_value}
        />
      )
    }
    return (
      <MultipleChoiceInput
        label={label}
        options={this.props.parameter_values}
        placeholder={this.props.placeholder}
        readOnly={this.props.readOnly}
        required={this.props.required}
        set_value={(value) => this.set_source_parameter(this.props.parameter_key, value)}
        value={this.props.parameter_value || []}
      />
    )
  }
}

export { SourceParameter };
