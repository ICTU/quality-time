import React, { Component } from 'react';
import { Form, Label } from 'semantic-ui-react';


class MetricTarget extends Component {
  constructor(props) {
    super(props);
    this.state = { edited_target: this.props.target }
  }
  onChange(event) {
    this.setState({ edited_target: event.target.value || 0});
  }
  onKeyDown(event) {
    if (event.key === "Escape") {
      this.setState({ edited_target: this.props.target })
    }
  }
  onSubmit(event) {
    event.preventDefault();
    if (this.state.edited_target !== this.props.target) {
      this.props.set_metric_attribute("target", this.state.edited_target || 0);
    }
  }
  render() {
    return (
      <Form onSubmit={(e) => this.onSubmit(e)}>
        <Form.Group style={{marginBottom: '0px'}}>
          <Form.Input width={16} label='Metric target' focus type="number" min="0" value={this.state.edited_target || 0}
            onChange={(e) => this.onChange(e)} onKeyDown={(e) => this.onKeyDown(e)} onBlur={(e) => this.onSubmit(e)}
            labelPosition='right' readOnly={(this.props.user === null)}>
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
