import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';

class TextInput extends Component {
  constructor(props) {
    super(props);
    this.state = { edited_text: props.value }
  }
  onChange(event) {
    this.setState({ edited_text: event.target.value });
  }
  onKeyDown(event) {
    if (event.key === "Escape") {
      this.setState({ edited_text: this.props.value })
    }
  }
  onKeyPress(event) {
    if (event.key === "Enter" && event.shiftKey) {
      this.onSubmit(event);
    }
  }
  onSubmit(event) {
    event.preventDefault();
    const edited_text = this.state.edited_text || "";
    if (edited_text !== this.props.value) {
      this.props.set_value(edited_text);
    }
  }
  render() {
    return (
      <Form onSubmit={(e) => this.onSubmit(e)}>
        <Form.TextArea
          label={this.props.label}
          onBlur={(e) => this.onSubmit(e)}
          onChange={(e) => this.onChange(e)}
          onKeyDown={(e) => this.onKeyDown(e)}
          onKeyPress={(e) => this.onKeyPress(e)}
          readOnly={this.props.readOnly}
          value={this.state.edited_text}
        />
      </Form>
    )
  }
}

export { TextInput };
