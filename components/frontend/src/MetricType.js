import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';

class MetricType extends Component {
  constructor(props) {
    super(props);
    this.state = { edited_metric_type: props.metric_type };
  }
  onKeyDown(event) {
    if (event.key === "Escape") {
      this.setState({ edited_metric_type: this.props.metric_type });
    }
  }
  onSubmit(event, { name, value }) {
    event.preventDefault();
    let self = this;
    this.setState({ edited_metric_type: value });
    fetch(`http://localhost:8080/report/${this.props.report_uuid}/metric/${this.props.metric_uuid}/type`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ type: value })
    }).then(() => self.props.reload());
  }
  render() {
    let options = [];
    let self = this;
    Object.keys(this.props.datamodel.metrics).forEach(
      (key) => { options.push({ text: self.props.datamodel.metrics[key].name, value: key }) });
    return (
      <Form>
        {this.props.user === null ?
        <Form.Input label='Metric type' readOnly
          value={self.props.datamodel.metrics[this.state.edited_metric_type].name} />
      :
        <Form.Dropdown label='Metric type' search fluid selection selectOnNavigation={false}
          value={this.state.edited_metric_type}
          options={options} onChange={(e, { name, value }) => this.onSubmit(e, { name, value })} tabIndex="0" />
      }
      </Form>
    )
  }
}

export { MetricType };
