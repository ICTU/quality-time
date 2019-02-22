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
    fetch(`http://localhost:8080/measurement/${this.props.metric_uuid}/source/${source_uuid}/unit/${unit_key}/ignore`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    })
    .then(function(response) { return response.json(); })
    .then(function(json) {
      let measurements = self.state.measurements.slice(0);
      measurements.push(json)
      self.setState({ measurements: measurements})
    })
  }
  fetch_measurement() {
    let self = this;
    const report_date = this.props.report_date ? this.props.report_date : new Date();
    fetch(`http://localhost:8080/measurements/${this.props.metric_uuid}&report_date=${report_date.toISOString()}`)
      .then(function (response) {
        return response.json();
      })
      .then(function (json) {
        self.setState({ measurements: json.measurements });
      })
  }
  onEdit(event) {
    event.preventDefault();
    this.fetch_measurement();
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
    const metric_name = this.props.datamodel.metrics[this.props.metric.type].name;
    if (search && !metric_name.toLowerCase().includes(search.toLowerCase())) { return null };
    return (
      <Measurement report_uuid={this.props.report_uuid} metric_uuid={this.props.metric_uuid}
        nr_new_measurements={this.props.nr_new_measurements} datamodel={this.props.datamodel}
        reload={this.props.reload} metric={this.props.metric}
        measurements={this.state.measurements} onEdit={(e) => this.onEdit(e)}
        ignore_unit={(e, s, u) => this.ignore_unit(e, s, u)} />
    )
  }
}

export default Metric;
