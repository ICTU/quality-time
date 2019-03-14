import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';

class PasswordParameter extends Component {
  constructor(props) {
    super(props);
    this.state = { edited_value: this.props.parameter_value }
  }
  componentDidUpdate(prevProps) {
    if (prevProps.parameter_value !== this.props.parameter_value) {
      this.setState({ edited_value: this.props.parameter_value })
    }
  }
  onChange(event) {
    this.setState({ edited_value: event.target.value });
  }
  onKeyDown(event) {
    if (event.key === "Escape") {
      this.setState({ edited_value: this.props.parameter_value })
    }
  }
  onSubmit(event) {
    event.preventDefault();
    if (this.state.edited_value !== this.props.parameter_value) {
      this.props.set_parameter(this.props.parameter_key, this.state.edited_value);
    }
  }
  render() {
    return (
      <Form>
        <Form.Input
          fluid
          focus
          label={this.props.parameter_name}
          onBlur={(e) => this.onSubmit(e)}
          onChange={(e) => this.onChange(e)}
          onKeyDown={(e) => this.onKeyDown(e)}
          onSubmit={(e) => this.onSubmit(e)}
          placeholder={this.props.placeholder}
          readOnly={this.props.readOnly}
          type="password"
          value={this.state.edited_value || ""}
        />
      </Form>
    )
  }
}

export { PasswordParameter };
