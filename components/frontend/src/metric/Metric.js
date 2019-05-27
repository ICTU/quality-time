import React, { Component } from 'react';
import { Measurement } from './Measurement';

class Metric extends Component {
  constructor(props) {
    super(props);
    this.state = { measurements: [] }
  }
  fetch_measurement_and_reload() {
    this.fetch_measurement()
    this.props.reload()
  }
  fetch_measurement() {
    let self = this;
    const report_date = this.props.report_date || new Date(3000, 12, 31);
    fetch(`${window.server_url}/measurements/${this.props.metric_uuid}?report_date=${report_date.toISOString()}`)
      .then(function (response) {
        return response.json();
      })
      .then(function (json) {
        self.setState({ measurements: json.measurements });
        const last_measurement = json.measurements && json.measurements.length > 0 ? json.measurements[json.measurements.length - 1] : null;
        self.props.set_last_measurement(self.props.metric_uuid, last_measurement);
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
        fetch_measurement_and_reload={() => this.fetch_measurement_and_reload()}
        report={this.props.report}
        readOnly={this.props.readOnly}
        subject_uuid={this.props.subject_uuid}
      />
    )
  }
}

export { Metric };
