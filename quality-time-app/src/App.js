import React, { Component } from 'react';
import './App.css';
import { Subject } from './Subject.js';
import { Container, Header, Input } from 'semantic-ui-react';


class App extends Component {
  constructor(props) {
    super(props);
    this.state = {subjects: [], search_string: ''};
    this.handleSearchChange = this.handleSearchChange.bind(this);
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

  handleSearchChange(event) {
    this.setState({search_string: event.target.value});
  }

  render() {
    return (
      <Container>
        <Header as='h1' textAlign='center'>Quality-time</Header>
        <Input placeholder='Filter metrics...' onChange={this.handleSearchChange} />
        <Container>
          {this.state.subjects.map((subject) =>
            <Subject key={subject.title} title={subject.title} metrics={subject.metrics}
                     search_string={this.state.search_string} />)}
        </Container>
      </Container>
    );
  }
}

export default App;
