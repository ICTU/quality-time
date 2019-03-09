import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';


class MetricName extends Component {
  constructor(props) {
    super(props);
    this.state = { edited_name: props.metric_name }
  }
  componentDidUpdate(prevProps) {
    if (prevProps.metric_name !== this.props.metric_name ) {
      this.setState({ edited_name: this.props.metric_name })
    }
  }
  onChange(event) {
    this.setState({ edited_name: event.target.value });
  }
  onKeyDown(event) {
    if (event.key === "Escape") {
      this.setState({ edited_name: this.props.metric_name })
    }
  }
  onSubmit(event) {
    event.preventDefault();
    if (this.state.edited_name !== this.props.metric_name) {
      this.props.set_metric_attribute("name", this.state.edited_name);
    }
  }
  render() {
    return (
      <Form onSubmit={(e) => this.onSubmit(e)}>
        <Form.Input label="Metric name" focus fluid value={this.state.edited_name}
          readOnly={(this.props.user === null)}
          placeholder={this.props.metric_type_name} onBlur={(e) => this.onSubmit(e)}
          onChange={(e) => this.onChange(e)} onKeyDown={(e) => this.onKeyDown(e)} />
      </Form>
    )
  }
}

export { MetricName };
