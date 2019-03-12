import React, { Component } from 'react';
import { StringParameter } from './StringParameter.js';
import { MultipleChoiceParameter } from './MultipleChoiceParameter.js';

class SourceParameter extends Component {
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
    if (this.props.parameter_type === "string") {
      // Collect all values in the current report used for this parameter, for this source type:
      let values = [];
      Object.values(this.props.report.subjects).forEach((subject) => {
        Object.values(subject.metrics).forEach((metric) => {
          Object.values(metric.sources).forEach((source) => {
            if (source.type === this.props.source.type && source.parameters) {
              const value = source.parameters[this.props.parameter_key];
              if (value && values.indexOf(value) === -1) {
                values.push(source.parameters[this.props.parameter_key]);
              }
            }
          })
        })
      });
      const options = values.sort().map((value) => ({ key: value, value: value, text: value }));
      return (
        <StringParameter
          parameter_key={this.props.parameter_key} parameter_name={this.props.parameter_name}
          options={options} parameter_value={this.props.parameter_value}
          set_parameter={(key, value) => this.set_source_parameter(key, value)}
          readOnly={this.props.readOnly} label={this.props.parameter_name} placeholder={this.props.placeholder} />
      )
    };
    return (
      <MultipleChoiceParameter
        parameter_key={this.props.parameter_key} parameter_name={this.props.parameter_name}
        parameter_value={this.props.parameter_value} parameter_values={this.props.parameter_values}
        set_parameter={(key, value) => this.set_source_parameter(key, value)}
        readOnly={this.props.readOnly} label={this.props.parameter_name} />
    )
  }
}

export { SourceParameter };
