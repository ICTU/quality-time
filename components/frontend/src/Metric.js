import React, { Component } from 'react';
import Measurement from './Measurement.js';


class Metric extends Component {
  constructor(props) {
    super(props);
    this.state = { measurements: [] }
  }
  set_unit_attribute(source_uuid, unit_key, attribute, value) {
    const self = this;
    fetch(`${window.server_url}/measurement/${this.props.metric_uuid}/source/${source_uuid}/unit/${unit_key}/${attribute}`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({[attribute]: value})
    })
      .then(function (response) { return response.json(); })
      .then(function (json) {
        self.fetch_measurement();
        self.props.reload();
      })
  }
  set_metric_attribute(attribute, value) {
    const self = this;
    fetch(`${window.server_url}/report/${this.props.report.report_uuid}/metric/${this.props.metric_uuid}/${attribute}`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ [attribute]: value })
    })
      .then(function (response) {
        return response.json();
      })
      .then(function (json) {
        if (attribute === "target" || attribute === "near_target" || attribute === "debt_target" || attribute === "accept_debt") {
          self.fetch_measurement();
        }
        self.props.reload();
      })
      .catch(function(error) {
        console.log(error);
      })
  }
  fetch_measurement() {
    let self = this;
    const report_date = this.props.report_date ? this.props.report_date : new Date();
    fetch(`${window.server_url}/measurements/${this.props.metric_uuid}?report_date=${report_date.toISOString()}`)
      .then(function (response) {
        return response.json();
      })
      .then(function (json) {
        self.setState({ measurements: json.measurements });
      })
  }
  componentDidMount() {
    this.fetch_measurement();
  }
  componentDidUpdate(prevProps) {
    if (prevProps.report_date !== this.props.report_date ||
      (prevProps.nr_new_measurements !== 0 && this.props.nr_new_measurements === 0)) {
      this.fetch_measurement();
    }
  }
  render() {
    const search = this.props.search_string;
    const metric = this.props.report.subjects[this.props.subject_uuid].metrics[this.props.metric_uuid];
    const metric_name = metric.name || this.props.datamodel.metrics[metric.type].name;
    if (search && !metric_name.toLowerCase().includes(search.toLowerCase())) { return null };
    return (
      <Measurement
        datamodel={this.props.datamodel}
        measurements={this.state.measurements}
        metric_uuid={this.props.metric_uuid}
        nr_new_measurements={this.props.nr_new_measurements}
        reload={this.props.reload}
        report={this.props.report}
        readOnly={this.props.readOnly}
        set_metric_attribute={(a, v) => this.set_metric_attribute(a, v)}
        set_unit_attribute={(s, u, a, v) => this.set_unit_attribute(s, u, a, v)}
        subject_uuid={this.props.subject_uuid}
      />
    )
  }
}

export default Metric;
