import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';

class MultipleChoiceParameter extends Component {
  options() {
    return this.props.parameter_values.map((value) => ({ key: value, text: value, value: value }));
  }
  onSubmit(event, value) {
    event.preventDefault();
    if (value !== this.props.parameter_value) {
      this.props.set_parameter(this.props.parameter_key, value);
    }
  }
  render() {
    return (
      <Form >
        {this.props.readOnly ?
          <Form.Input label={this.props.label} value={this.props.parameter_value} readOnly />
          :
          <Form.Dropdown label={this.props.label}
            value={this.props.parameter_value || []} onChange={(e, { value }) => this.onSubmit(e, value)}
            fluid multiple selection options={this.options()} />
        }
      </Form>
    )
  }
}

export { MultipleChoiceParameter };
