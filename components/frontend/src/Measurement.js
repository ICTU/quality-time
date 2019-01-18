import React, { Component } from 'react';
import { Table, Popup } from 'semantic-ui-react';
import TimeAgo from 'react-timeago';
import { Comment } from './Comment';
import { Source } from './Source';
import { Target } from './Target';
import { TrendSparkline } from './TrendSparkline';


class Measurement extends Component {
  constructor(props) {
    super(props);
    this.state = {hover: false, measurements: [], metric: {}}
  }
  componentDidMount() {
    let self = this;
    const last_measurement = this.props.measurements[this.props.measurements.length - 1];
    const metric_name = last_measurement.request.metric;
    fetch(`http://localhost:8080/metric/${metric_name}`)
    .then(function(response) {
      return response.json();
    })
    .then(function(json) {
      self.setState({metric: json});
    });
  }
  onMouseEnter(event) {
    this.setState({hover: true})
  }
  onMouseLeave(event) {
    this.setState({hover: false})
  }
  render() {
    const last_measurement = this.props.measurements[this.props.measurements.length - 1];
    const metric_id = last_measurement.request.request_url;
    const measurement = last_measurement.measurement;
    const sources = last_measurement.sources;
    const start = new Date(measurement.start);
    const end = new Date(measurement.end);
    return (
      <Table.Row positive={measurement.status === "target_met"}
                negative={measurement.status === "target_not_met"}
                warning={measurement.status === null}
                onMouseEnter={(e) => this.onMouseEnter(e)}
                onMouseLeave={(e) => this.onMouseLeave(e)}>
        <Table.Cell>
          {this.state.metric.name}
        </Table.Cell>
        <Table.Cell>
          <TrendSparkline measurements={this.props.measurements} />
        </Table.Cell>
        <Popup
          trigger={
            <Table.Cell>
              {(measurement.measurement === null ? '?' : measurement.measurement) + ' ' + this.state.metric.unit}
            </Table.Cell>
          }
          flowing hoverable>
          Measured <TimeAgo date={measurement.end} /> ({start.toLocaleString()} - {end.toLocaleString()})
        </Popup>
        <Table.Cell>
          <Target metric_id={metric_id} editable={this.state.hover} direction={this.state.metric.direction}
                  target={measurement.target} unit={this.state.metric.unit} key={end} onEdit={this.props.onEdit} />
        </Table.Cell>
        <Table.Cell>
          {sources.map((source) => <Source key={source.api_url} source={source} />)}
        </Table.Cell>
        <Table.Cell>
          <Comment metric_id={metric_id} editable={this.state.hover}
                   comment={last_measurement.comment} key={end} />
        </Table.Cell>
      </Table.Row>
    )
  }
}

export default Measurement;
