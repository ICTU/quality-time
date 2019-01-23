import React, { Component } from 'react';
import { Icon, Table, Popup, Segment } from 'semantic-ui-react';
import TimeAgo from 'react-timeago';
import { Comment } from './Comment';
import { Source } from './Source';
import { Target } from './Target';
import { TrendGraph } from './TrendGraph';
import { TrendSparkline } from './TrendSparkline';


function DetailPanel(props) {
  return (
    <Table.Row>
      <Table.Cell colSpan="6">
        <Segment.Group horizontal>
          <Segment>
            <TrendGraph measurements={props.measurements} unit={props.unit} />
          </Segment>
          <Segment>
            Another segment.
          </Segment>
          <Segment>
            Another segment.
          </Segment>
        </Segment.Group>
      </Table.Cell>
    </Table.Row>
  )
}

class Measurement extends Component {
  constructor(props) {
    super(props);
    this.state = { hover: false, measurements: [], metric: {}, show_details: false }
  }
  componentDidMount() {
    let self = this;
    const last_measurement = this.props.measurements[this.props.measurements.length - 1];
    const metric_name = last_measurement.request.metric;
    fetch(`http://localhost:8080/metric/${metric_name}`)
      .then(function (response) {
        return response.json();
      })
      .then(function (json) {
        self.setState({ metric: json });
      });
  }
  onMouseEnter(event) {
    this.setState({ hover: true })
  }
  onMouseLeave(event) {
    this.setState({ hover: false })
  }
  onExpand(event) {
    this.setState((state) => ({show_details: !state.show_details}));
  }
  render() {
    const last_measurement = this.props.measurements[this.props.measurements.length - 1];
    const metric_id = last_measurement.request.request_url;
    const measurement = last_measurement.measurement;
    const sources = last_measurement.sources;
    const start = new Date(measurement.start);
    const end = new Date(measurement.end);
    const positive = measurement.status === "target_met";
    const negative = measurement.status === "target_not_met";
    const warning = measurement.status === null;
    return (
      <>
        <Table.Row positive={positive} negative={negative} warning={warning}
          onMouseEnter={(e) => this.onMouseEnter(e)}
          onMouseLeave={(e) => this.onMouseLeave(e)}>
          <Table.Cell>
            <Icon name={this.state.show_details ? "caret down" : "caret right"} onClick={(e) => this.onExpand(e)} />
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
        {this.state.show_details && <DetailPanel measurements={this.props.measurements} unit={this.state.metric.unit} />}
      </>
    )
  }
}

export default Measurement;
