import React, { Component } from 'react';
import { StringParameter} from './StringParameter.js';
import { MultipleChoiceParameter} from './MultipleChoiceParameter.js';

class SourceParameter extends Component {
  set_source_parameter(key, value) {
    fetch(`${window.server_url}/report/${this.props.report_uuid}/source/${this.props.source_uuid}/parameter/${key}`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ [key]: value })
    }).then(() => this.props.reload())
  }
  render() {
    return (
      this.props.parameter_type === "string" ?
        <StringParameter
          parameter_key={this.props.parameter_key} parameter_name={this.props.parameter_name}
          parameter_value={this.props.parameter_value}
          set_parameter={(key, value ) => this.set_source_parameter(key, value)}
          readOnly={this.props.readOnly} label={this.props.parameter_name} placeholder={this.props.placeholder} />
        :
        <MultipleChoiceParameter
          parameter_key={this.props.parameter_key} parameter_name={this.props.parameter_name}
          parameter_value={this.props.parameter_value} parameter_values={this.props.parameter_values}
          set_parameter={(key, value) => this.set_source_parameter(key, value)}
          readOnly={this.props.readOnly} label={this.props.parameter_name} />
    )
  }
}

export { SourceParameter };
