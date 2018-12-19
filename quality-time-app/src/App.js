import React, { Component } from 'react';
import './App.css';
import { Subject } from './Subject.js';
import { Container } from 'semantic-ui-react';


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
        self.setState({subjects: json.subjects});
      });
  }

  render() {
    return (
      <Container>
        <h1>Quality-time</h1>
        <div>
          {this.state.subjects.map((subject) =>
            <Subject key={subject.title} title={subject.title} metrics={subject.metrics}/>)}
        </div>
      </Container>
    );
  }
}

export default App;
