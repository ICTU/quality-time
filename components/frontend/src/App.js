import React, { Component } from 'react';
import './App.css';
import { Container, Form, Label, Header, Input } from 'semantic-ui-react';
import { DateInput } from 'semantic-ui-calendar-react';
import { Subject } from './Subject.js';
import { Menubar } from './Menubar.js';


function NewMeasurementsLabel(props) {
  if (props.nr_new_measurements === 0) {return null}
  const plural_s = props.nr_new_measurements > 1 ? 's' : '';
  return (
    <Label as='a' tag color='blue' onClick={props.onClick}>{props.nr_new_measurements} new measurement{plural_s} available</Label>
  )
}


class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      subjects: [], search_string: '', report_date_string: '', nr_measurements: 0, nr_new_measurements: 0
    };
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
      const nr_measurements = Number(e.data);
      self.setState({nr_measurements: nr_measurements, nr_new_measurements: 0});
    }, false);
    source.addEventListener('delta', function(e) {
      self.setState({nr_new_measurements: Number(e.data) - self.state.nr_measurements});
    }, false);
    source.addEventListener('error', function(e) {
      if (e.readyState === EventSource.CLOSED) {
        self.setState({nr_measurements: 0, nr_new_measurements: 0});
      }
      else if (e.readyState === EventSource.OPEN) {
        self.setState({nr_measurements: 0, nr_new_measurements: 0});
      }
    }, false);
  }

  reload(event) {
    event.preventDefault();
    let self = this;
    fetch('http://localhost:8080/report')
      .then(function(response) {
        return response.json();
      })
      .then(function(json) {
        const nr_measurements = self.state.nr_measurements + self.state.nr_new_measurements;
        self.setState(
          {
            subjects: json.subjects,
            report_date_string: '',
            nr_measurements: nr_measurements,
            nr_new_measurements: 0
          }
        );
      }
    );
  }

  handleSearchChange(event) {
    this.setState({search_string: event.target.value});
  }

  handleDateChange = (event, {name, value}) => {
    if (this.state.hasOwnProperty(name)) {
      this.setState({[name]: value})
    }
  }

  render() {
    const today = new Date();
    const today_string = today.getDate() + '-' + (today.getMonth() + 1) + '-' + today.getFullYear();
    let report_date = new Date();
    if (this.state.report_date_string) {
      report_date = new Date(this.state.report_date_string.split("-").reverse().join("-"));
      report_date.setHours(23, 59, 59);
    }
    return (
      <div>
        <Menubar />
        <Container style={{ marginTop: '7em' }}>
          <Header as='h1' textAlign='center'>
            Quality-time <NewMeasurementsLabel onClick={(e)=>this.reload(e)} nr_new_measurements={this.state.nr_new_measurements} />
          </Header>
          <Form>
            <Form.Group>
              <Form.Field>
                <label>Filter metrics</label>
                <Input icon='search' iconPosition='left' placeholder='Search...' onChange={this.handleSearchChange} />
              </Form.Field>
              <Form.Field>
                <label>Report date</label>
                <DateInput name="report_date_string" value={this.state.report_date_string}
                           placeholder={today_string} closable={true} initialDate={today}
                           maxDate={today} iconPosition="left" onChange={this.handleDateChange} />
              </Form.Field>
            </Form.Group>
          </Form>
          <Container>
            {this.state.subjects.map((subject) =>
              <Subject key={subject.title} title={subject.title} metrics={subject.metrics}
                       search_string={this.state.search_string} report_date={report_date}/>)}
          </Container>
        </Container>
      </div>
    );
  }
}

export default App;
