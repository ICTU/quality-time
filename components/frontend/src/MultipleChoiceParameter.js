import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';

class MultipleChoiceParameter extends Component {
  onSubmit(event, value) {
    event.preventDefault();
    if (value !== this.props.parameter_value) {
      this.props.set_parameter(this.props.parameter_key, value);
    }
  }
  render() {
    const options = this.props.parameter_values.map((value) => ({ key: value, text: value, value: value }));
    return (
      <Form >
        {this.props.readOnly ?
          <Form.Input label={this.props.parameter_name} value={this.props.parameter_value} readOnly />
          :
          <Form.Dropdown label={this.props.parameter_name}
            defaultValue={this.props.parameter_value} onChange={(e, { value }) => this.onSubmit(e, value)}
            fluid multiple selection options={options} />
        }
      </Form>
    )
  }
}

export { MultipleChoiceParameter };
