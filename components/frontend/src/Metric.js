import React, { Component } from 'react';
import { Placeholder } from 'semantic-ui-react';
import Measurement from './Measurement.js';


class Metric extends Component {
  constructor(props) {
    super(props);
    this.state = {measurement: null, metric: null, source: null}
  }
  fetch_measurement() {
    let report_date = new Date();
    if (this.props.report_date !== '') {
      const parts = this.props.report_date.split(" ");
      const date_parts = parts[0].split("-");
      report_date.setFullYear(date_parts[2]);
      report_date.setMonth(Number(date_parts[1]) - 1);
      report_date.setDate(date_parts[0]);
      if (parts.length > 1) {
        const time_parts = parts[1].split(":");
        report_date.setHours(time_parts[0], time_parts[1]);
      }
    }
    const iso_report_date = report_date.toISOString().split(".")[0];
    let self = this;
    fetch(`http://localhost:8080/${this.props.metric}&report_date=${iso_report_date}`)
      .then(function(response) {
        return response.json();
      })
      .then(function(json) {
        self.setState({measurement: json.measurement, metric: json.metric, source: json.source});
      });
  }
  componentDidMount() {
    this.fetch_measurement();
  }
  componentDidUpdate(prevProps) {
    if (prevProps.report_date !== this.props.report_date) {
      console.log(`Fetching measurement for ${this.props.report_date}`);
      this.fetch_measurement();
    }
  }
  render() {
    const m = this.state.metric;
    if (m === null) {
      return (
        <Placeholder>
          <Placeholder.Line />
          <Placeholder.Line />
        </Placeholder>
      )
    }
    const search = this.props.search_string;
    if (search && !m.name.toLowerCase().includes(search.toLowerCase())) {return null};
    return (
      <Measurement measurement={this.state.measurement} metric={this.state.metric} source={this.state.source} />
    )
  }
}

export default Metric;
