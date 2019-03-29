import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';

class Input extends Component {
  constructor(props) {
    super(props);
    this.state = { edited_value: this.props.value }
  }
  componentDidUpdate(prevProps) {
    if (prevProps.value !== this.props.value) {
      this.setState({ edited_value: this.props.value })
    }
  }
  onChange(event) {
    this.setState({ edited_value: event.target.value });
  }
  onKeyDown(event) {
    if (event.key === "Escape") {
      this.setState({ edited_value: this.props.value })
    }
  }
  onSubmit(event) {
    event.preventDefault();
    if (this.state.edited_value !== this.props.value) {
      this.props.set_value(this.state.edited_value);
    }
  }
  render() {
    let { set_value, ...props } = this.props;
    return (
      <Form>
        <Form.Input
          {...props}
          fluid
          focus
          onBlur={(e) => this.onSubmit(e)}
          onChange={(e) => this.onChange(e)}
          onKeyDown={(e) => this.onKeyDown(e)}
          onSubmit={(e) => this.onSubmit(e)}
          value={this.state.edited_value || ""}
        />
      </Form>
    )
  }
}

export { Input };
