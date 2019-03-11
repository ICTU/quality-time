import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';

class SingleChoiceParameter extends Component {
  constructor(props) {
    super(props);
    this.state = { edited_parameter_value: props.parameter_value };
  }
  onKeyDown(event) {
    if (event.key === "Escape") {
      this.setState({ edited_parameter_value: this.props.parameter_value });
    }
  }
  onSubmit(event, { name, value }) {
    event.preventDefault();
    this.setState({ edited_parameter_value: value });
    if (value !== this.props.parameter_value) {
      this.props.set_parameter(this.props.parameter_key, value);
    }
  }
  render() {
    const parameter_value_name = this.props.parameter_values.filter(({text, value}) => value === this.props.parameter_value)[0].text;
    return (
      <Form>
        {this.props.readOnly ?
          <Form.Input label={this.props.parameter_name} value={parameter_value_name} readOnly />
          :
          <Form.Dropdown label={this.props.parameter_name} search fluid selection selectOnNavigation={false}
            value={this.state.edited_parameter_value} options={this.props.parameter_values}
            onChange={(e, { name, value }) => this.onSubmit(e, { name, value })} tabIndex="0" />
        }
      </Form>
    )
  }
}

export { SingleChoiceParameter };
