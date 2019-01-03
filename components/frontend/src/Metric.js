import React, { Component } from 'react';
import { Placeholder, Table } from 'semantic-ui-react';
import Measurement from './Measurement.js';


class Metric extends Component {
  constructor(props) {
    super(props);
    this.state = {measurement: null, metric: null, source: null}
  }
  fetch_measurement() {
    const iso_report_date = this.props.report_date.toISOString().split(".")[0];
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
      this.fetch_measurement();
    }
  }
  render() {
    const m = this.state.metric;
    if (m === null) {
      return (
        <Table.Row>
          <Table.Cell>
            <Placeholder>
              <Placeholder.Line />
              <Placeholder.Line />
            </Placeholder>
          </Table.Cell>
          <Table.Cell>
            <Placeholder>
              <Placeholder.Line />
              <Placeholder.Line />
            </Placeholder>
          </Table.Cell>
          <Table.Cell>
            <Placeholder>
              <Placeholder.Line />
              <Placeholder.Line />
            </Placeholder>
          </Table.Cell>
          <Table.Cell>
            <Placeholder>
              <Placeholder.Line />
              <Placeholder.Line />
            </Placeholder>
          </Table.Cell>
        </Table.Row>
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
