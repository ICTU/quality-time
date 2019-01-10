import React, { Component } from 'react';
import { Form, Icon, Table, Popup } from 'semantic-ui-react';
import TimeAgo from 'react-timeago';
import { Source } from './Source';
import { TrendSparkline } from './TrendSparkline';


class Comment extends Component {
  constructor(props) {
    super(props);
    this.state = {comment: "", edit: false}
  }
  componentDidMount() {
    let self = this;
    fetch(`http://localhost:8080/comment/${this.props.metric_id}`)
      .then(function(response) {
        return response.json();
      })
      .then(function(json) {
        self.setState({comment: json.comment});
      });
  }
  onClick() {
    this.setState({edit: true});
  }
  onChange(event) {
    this.setState({comment: event.target.value});
  }
  onSubmit(event) {
    event.preventDefault();
    this.setState({edit: false});
    fetch(`http://localhost:8080/comment/${this.props.metric_id}`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({comment: this.state.comment})
    }).then(result=>result.json())
  }
  render() {
    if (this.state.edit) {
      return (
        <Form onSubmit={(e) => this.onSubmit(e)}>
          <Form.Input autoFocus focus fluid value={this.state.comment} onChange={(e) => this.onChange(e)} />
        </Form>
      )
    }
    const style = this.state.comment ? {marginRight: "10px"} : {marginRight: "0px"};
    return (
      <div onClick={(e) => this.onClick(e)}>
        <span style={style}>
          {this.state.comment}
        </span>
        <Icon color='grey' name='edit' />
      </div>
    )
  }
}

function Measurement(props) {
  const last_measurement = props.measurements[props.measurements.length - 1];
  const metric_id = last_measurement.request.request_url;
  const metric = last_measurement.metric;
  const measurement = last_measurement.measurement;
  const source = last_measurement.source;
  const start = new Date(measurement.start);
  const end = new Date(measurement.end);
  return (
    <Table.Row positive={measurement.status === "target_met"}
              negative={measurement.status === "target_not_met"}
              warning={measurement.status === null}>
      <Table.Cell>
        {metric.name}
      </Table.Cell>
      <Table.Cell>
        <TrendSparkline measurements={props.measurements} />
      </Table.Cell>
      <Popup trigger={<Table.Cell>{(measurement.measurement === null ? '?' : measurement.measurement) + ' ' + metric.unit}</Table.Cell>} flowing hoverable>
        Measured <TimeAgo date={measurement.end} /> ({start.toLocaleString()} - {end.toLocaleString()})
      </Popup>
      <Table.Cell>
          {metric.direction} {measurement.target} {metric.unit}
      </Table.Cell>
      <Table.Cell>
        {source.responses.map((response) => <Source key={response.api_url} source={source.name} source_response={response} />)}
      </Table.Cell>
      <Table.Cell>
        <Comment metric_id={metric_id} />
      </Table.Cell>
    </Table.Row>
  )
}

export default Measurement;
