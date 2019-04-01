import React, { Component } from 'react';
import { Form, Label } from 'semantic-ui-react';


class MetricTarget extends Component {
  constructor(props) {
    super(props);
    this.state = { edited_target: this.props.target || 0 }
  }
  componentDidUpdate(prevProps) {
    if (prevProps.target !== this.props.target) {
      this.setState({ edited_target: this.props.target })
    }
  }
  onChange(event) {
    this.setState({ edited_target: event.target.value});
  }
  onKeyDown(event) {
    if (event.key === "Escape") {
      this.setState({ edited_target: this.props.target })
    }
  }
  onSubmit(event) {
    event.preventDefault();
    if (this.state.edited_target !== this.props.target) {
      this.props.set_value(this.state.edited_target || 0);
    }
  }
  render() {
    return (
      <Form onSubmit={(e) => this.onSubmit(e)}>
        <Form.Group style={{marginBottom: '0px'}}>
          <Form.Input
            focus
            label={this.props.label}
            labelPosition='right'
            min="0"
            type="number"
            onBlur={(e) => this.onSubmit(e)}
            onChange={(e) => this.onChange(e)}
            onKeyDown={(e) => this.onKeyDown(e)}
            readOnly={this.props.readOnly}
            value={this.state.edited_target}
            width={16}
          >
            <Label basic>{this.props.direction}</Label>
            <input />
            <Label basic>{this.props.unit}</Label>
          </Form.Input>
        </Form.Group>
      </Form >
    )
  }
}

export { MetricTarget };
