import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';


class MetricName extends Component {
  constructor(props) {
    super(props);
    this.state = { edited_name: props.metric_name }
  }
  componentDidUpdate(prevProps) {
    if (prevProps.metric_name !== this.props.metric_name) {
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
    const self = this;
    fetch(`http://localhost:8080/report/${this.props.report_uuid}/metric/${this.props.metric_uuid}/name`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name: this.state.edited_name })
    }).then(
      () => self.props.reload()
    )
  }
  render() {
    return (
      <Form onSubmit={(e) => this.onSubmit(e)}>
        <Form.Input focus fluid defaultValue={this.state.edited_name}
          onChange={(e) => this.onChange(e)} onKeyDown={(e) => this.onKeyDown(e)} />
      </Form>
    )
  }
}

export { MetricName };
