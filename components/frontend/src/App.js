import React, { Component } from 'react';
import './App.css';
import { Subject } from './Subject.js';
import { Container, Form, Header, Input } from 'semantic-ui-react';
import { DateTimeInput } from 'semantic-ui-calendar-react';


class App extends Component {
  constructor(props) {
    super(props);
    this.state = {subjects: [], search_string: '', report_date: ''};
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
        <Header as='h1' textAlign='center'>Quality-time</Header>
        <Form>
          <Form.Group>
            <Form.Field>
              <label>Filter metrics</label>
              <Input icon='search' iconPosition='left' placeholder='Search...' onChange={this.handleSearchChange} />
            </Form.Field>
            <Form.Field>
              <label>Report date</label>
              <DateTimeInput name="report_date" placeholder={today_string} value={this.state.report_date} closable={true}
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
