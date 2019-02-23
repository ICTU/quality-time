import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';


class MetricTarget extends Component {
  constructor(props) {
    super(props);
    this.state = { edited_target: this.props.target }
  }
  onChange(event) {
    this.setState({ edited_target: event.target.value });
  }
  onKeyDown(event) {
    if (event.key === "Escape") {
      this.setState({ edited_target: this.props.target })
    }
  }
  onSubmit(event) {
    event.preventDefault();
    const self = this;
    fetch(`http://localhost:8080/report/${this.props.report_uuid}/metric/${this.props.metric_uuid}/target`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ target: this.state.edited_target })
    }).then(
      () => self.props.reload()
    )
  }
  render() {
    return (
      <Form onSubmit={(e) => this.onSubmit(e)}>
        <Form.Group style={{ alignItems: "center", marginBottom: '0px'}}>
          {this.props.direction}
          <Form.Input focus inline type="number" defaultValue={this.state.edited_target}
            onChange={(e) => this.onChange(e)} onKeyDown={(e) => this.onKeyDown(e)} />
          {this.props.unit}
        </Form.Group>
      </Form>
    )
  }
}

export { MetricTarget };
