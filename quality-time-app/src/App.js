import React, { Component } from 'react';
import './App.css';

function Subject(props) {
  return (
    <div>
      <h1>{props.title}</h1>
      <div>
        {props.metrics.map((metric) => <Metric key={metric} metric={metric} />)}
      </div>
    </div>
  )
}

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
    return (
      <Measurement measurement={this.state.measurement} />
    )
  }
}

function Measurement(props) {
  const m = props.measurement;
  if (m) {
    return (
      <div>
        Measurement: {m.measurement} {m.unit},
        Target: {m.target} {m.unit},
        Status: {m.status === "target_met" ? "💚" : "💔"}
      </div>
    )
  } else {
    return (
      <div>Measurement: unknown</div>
    )
  }
}

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {subjects: []};
  }

  componentDidMount() {
    let self = this;
    fetch('http://localhost:8080/report')
      .then(function(response) {
        return response.json();
      })
      .then(function(json) {
        console.log(json);
        self.setState({subjects: json.subjects});
      });
  }

  render() {
    return (
      <div className="App">
        <header className="App-header">
          Quality time
        </header>
        <div>
          {this.state.subjects.map((subject) =>
            <Subject key={subject.title} title={subject.title} metrics={subject.metrics}/>)}
        </div>
      </div>
    );
  }
}

export default App;
