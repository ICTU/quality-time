import React, { Component } from 'react';
import './App.css';
import { Subject } from './Subject.js';
import { Container, Form, Label, Header, Input } from 'semantic-ui-react';
import { DateInput } from 'semantic-ui-calendar-react';


class App extends Component {
  constructor(props) {
    super(props);
    this.state = {subjects: [], search_string: '', report_date: '', nr_measurements: '?'};
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

    var source = new EventSource("http://localhost:8080/nr_measurements");
    source.addEventListener('init', function(e) {
      self.setState({nr_measurements: e.data});
    }, false);
    source.addEventListener('delta', function(e) {
      self.setState({nr_measurements: e.data});
    }, false);
    source.addEventListener('error', function(e) {
      if (e.readyState === EventSource.CLOSED) {
        self.setState({nr_measurements: "X"});
      }
      else if( e.readyState === EventSource.OPEN) {
        self.setState({nr_measurements: "..."});
      }
    }, false);
  }

  handleSearchChange(event) {
    this.setState({search_string: event.target.value});
  }

  handleDateChange = (event, {name, value}) => {
    if (this.state.hasOwnProperty(name)) {
      this.setState({ [name]: value });
    }
  }

  render() {
    const today = new Date();
    const today_string = today.getDate() + '-' + (today.getMonth() + 1) + '-' + today.getFullYear();
    return (
      <Container>
        <Header as='h1' textAlign='center'>Quality-time <Label tag>{this.state.nr_measurements} measurements</Label>
        </Header>
        <Form>
          <Form.Group>
            <Form.Field>
              <label>Filter metrics</label>
              <Input icon='search' iconPosition='left' placeholder='Search...' onChange={this.handleSearchChange} />
            </Form.Field>
            <Form.Field>
              <label>Report date</label>
              <DateInput name="report_date" placeholder={today_string} value={this.state.report_date} closable={true}
                        initialDate={today} maxDate={today} iconPosition="left" onChange={this.handleDateChange} />
            </Form.Field>
          </Form.Group>
        </Form>
        <Container>
          {this.state.subjects.map((subject) =>
            <Subject key={subject.title} title={subject.title} metrics={subject.metrics}
                     search_string={this.state.search_string} report_date={this.state.report_date}/>)}
        </Container>
      </Container>
    );
  }
}

export default App;
