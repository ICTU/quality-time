import React, { Component } from 'react';
import Measurement from './Measurement.js';


class Metric extends Component {
  constructor(props) {
    super(props);
    this.state = {measurement: null}
  }
  componentDidMount() {
    let self = this;
    fetch('http://localhost:8080/' + this.props.metric)
      .then(function(response) {
        return response.json();
      })
      .then(function(json) {
        self.setState({measurement: json});
      });
  }
  render() {
    const m = this.state.measurement;
    if (m === null) {return null};
    const search = this.props.search_string;
    if (search && !m.metric.toLowerCase().includes(search.toLowerCase())) {return null};
    return (
      <Measurement measurement={this.state.measurement} />
    )
  }
}

export default Metric;
