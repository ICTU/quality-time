import React, { Component } from 'react';
import { Measurement } from './Measurement';
import { set_metric_attribute } from '../api/metric';

class Metric extends Component {
  constructor(props) {
    super(props);
    this.state = { measurements: [] }
  }
  set_entity_attribute(source_uuid, entity_key, attribute, value) {
    const self = this;
    fetch(`${window.server_url}/measurement/${this.props.metric_uuid}/source/${source_uuid}/entity/${entity_key}/${attribute}`, {
      method: 'post',
      credentials: 'include',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ [attribute]: value })
    })
      .then(function (response) { return response.json(); })
      .then(function (json) {
        self.fetch_measurement();
        self.props.reload();
      })
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
        report={this.props.report}
        readOnly={this.props.readOnly}
        set_metric_attribute={(a, v) => set_metric_attribute(this.props.report.report_uuid, this.props.metric_uuid, a, v, () => this.fetch_measurement_and_reload())}
        set_entity_attribute={(s, u, a, v) => this.set_entity_attribute(s, u, a, v)}
        subject_uuid={this.props.subject_uuid}
      />
    )
  }
}

export default Metric;
