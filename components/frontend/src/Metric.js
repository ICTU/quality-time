import React, { Component } from 'react';
import Measurement from './Measurement.js';


class Metric extends Component {
  constructor(props) {
    super(props);
    this.state = { measurements: [] }
  }
  ignore_unit(event, source_uuid, unit_key) {
    event.preventDefault();
    const self = this;
    fetch(`${window.server_url}/measurement/${this.props.metric_uuid}/source/${source_uuid}/unit/${unit_key}/ignore`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    })
      .then(function (response) { return response.json(); })
      .then(function (json) {
        self.fetch_measurement();
        self.props.reload();
      })
  }
  set_metric_attribute(attribute, value) {
    const self = this;
    fetch(`${window.server_url}/report/${this.props.report_uuid}/metric/${this.props.metric_uuid}/${attribute}`, {
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
        if (attribute === "target" || attribute === "debt_target") {
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
    const metric_name = this.props.metric.name || this.props.datamodel.metrics[this.props.metric.type].name;
    if (search && !metric_name.toLowerCase().includes(search.toLowerCase())) { return null };
    return (
      <Measurement report_uuid={this.props.report_uuid} metric_uuid={this.props.metric_uuid}
        nr_new_measurements={this.props.nr_new_measurements} datamodel={this.props.datamodel}
        reload={this.props.reload} metric={this.props.metric} user={this.props.user}
        measurements={this.state.measurements}
        set_metric_attribute={(a, v) => this.set_metric_attribute(a, v)}
        ignore_unit={(e, s, u) => this.ignore_unit(e, s, u)} />
    )
  }
}

export default Metric;
