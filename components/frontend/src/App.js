import React, { Component } from 'react';
import './App.css';
import { Subjects } from './Subjects.js';
import { Menubar } from './Menubar.js';


class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      datamodel: {}, subjects: {}, search_string: '', report_date_string: '',
      nr_measurements: 0, nr_new_measurements: 0
    };
    this.handleSearchChange = this.handleSearchChange.bind(this);
  }

  componentDidMount() {
    const report_date = this.props.report_date ? this.props.report_date : new Date();
    let self = this;
    fetch('http://localhost:8080/datamodel')
      .then(function (response) {
        return response.json();
      })
      .then(function (json) {
        self.setState({ datamodel: json });
      });
    fetch(`http://localhost:8080/report?report_date=${report_date.toISOString()}`)
      .then(function (response) {
        return response.json();
      })
      .then(function (json) {
        self.setState({ subjects: json.subjects });
      });
    var source = new EventSource("http://localhost:8080/nr_measurements");
    source.addEventListener('init', function (e) {
      self.setState({ nr_measurements: Number(e.data), nr_new_measurements: 0 });
    }, false);
    source.addEventListener('delta', function (e) {
      self.setState({ nr_new_measurements: Number(e.data) - self.state.nr_measurements });
    }, false);
    source.addEventListener('error', function (e) {
      if (e.readyState === EventSource.CLOSED) {
        self.setState({ nr_measurements: 0, nr_new_measurements: 0 });
      }
      else if (e.readyState === EventSource.OPEN) {
        self.setState({ nr_measurements: 0, nr_new_measurements: 0 });
      }
    }, false);
  }

  reload(event) {
    event.preventDefault();
    const report_date = this.props.report_date ? this.props.report_date : new Date();
    let self = this;
    fetch(`http://localhost:8080/report?report_date=${report_date.toISOString()}`)
      .then(function (response) {
        return response.json();
      })
      .then(function (json) {
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
    this.setState({ search_string: event.target.value });
  }

  handleDateChange = (event, { name, value }) => {
    if (this.state.hasOwnProperty(name)) {
      this.setState({ [name]: value })
    }
  }

  render() {
    let report_date = null;
    if (this.state.report_date_string) {
      report_date = new Date(this.state.report_date_string.split("-").reverse().join("-"));
      report_date.setHours(23, 59, 59);
    }
    return (
      <>
        <Menubar onSearch={this.handleSearchChange} onDate={this.handleDateChange}
          onReload={(e) => this.reload(e)} nr_new_measurements={this.state.nr_new_measurements}
          report_date={report_date} report_date_string={this.state.report_date_string} />
        <Subjects datamodel={this.state.datamodel} subjects={this.state.subjects}
          nr_new_measurements={this.state.nr_new_measurements}
          search_string={this.state.search_string} report_date={report_date} />
      </>
    );
  }
}

export default App;
