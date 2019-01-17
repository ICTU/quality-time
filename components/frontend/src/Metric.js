import React, { Component } from 'react';
import { Placeholder, Table } from 'semantic-ui-react';
import Measurement from './Measurement.js';


class Metric extends Component {
  constructor(props) {
    super(props);
    this.state = {measurements: []}
  }
  fetch_measurement() {
    let self = this;
    const report_date = this.props.report_date ? this.props.report_date : new Date();
    fetch(`http://localhost:8080/${this.props.metric}&report_date=${report_date.toISOString()}`)
      .then(function(response) {
        return response.json();
      })
      .then(function(json) {
        self.setState({measurements: json.measurements});
      });
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
    const m = this.state.measurements;
    if (m.length === 0) {
      return (
        <Table.Row>
          {[1, 2, 3, 4, 5, 6].map((index) =>
            <Table.Cell key={index}>
              <Placeholder>
                <Placeholder.Line />
                <Placeholder.Line />
              </Placeholder>
            </Table.Cell>)}
        </Table.Row>
      )
    }
    const search = this.props.search_string;
    let last_measurement = m[m.length - 1];
    if (search && !last_measurement["metric"].name.toLowerCase().includes(search.toLowerCase())) {return null};
    return (
      <Measurement measurements={m} onEdit={(e) => this.onEdit(e)} />
    )
  }
}

export default Metric;
