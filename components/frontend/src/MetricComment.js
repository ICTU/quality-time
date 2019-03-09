import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';

class MetricComment extends Component {
  constructor(props) {
    super(props);
    this.state = { edited_comment: props.comment }
  }
  onChange(event) {
    this.setState({ edited_comment: event.target.value });
  }
  onKeyDown(event) {
    if (event.key === "Escape") {
      this.setState({ edited_comment: this.props.comment })
    }
  }
  onKeyPress(event) {
    if (event.key === "Enter" && event.shiftKey) {
      this.onSubmit(event);
    }
  }
  onSubmit(event) {
    event.preventDefault();
    this.props.set_metric_attribute("comment", this.state.edited_comment || "");
  }
  render() {
    return (
      <Form onSubmit={(e) => this.onSubmit(e)}>
        <Form.TextArea label='Comment' readOnly={(this.props.user === null)}
          value={this.state.edited_comment} onBlur={(e) => this.onSubmit(e)}
          onChange={(e) => this.onChange(e)} onKeyDown={(e) => this.onKeyDown(e)}
          onKeyPress={(e) => this.onKeyPress(e)} />
      </Form>
    )
  }
}

export { MetricComment };
