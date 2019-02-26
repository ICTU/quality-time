import React, { Component } from 'react';
import { Container, Dimmer, Loader } from 'semantic-ui-react';
import { Report } from './Report.js';
import { Reports } from './Reports.js';
import { Menubar } from './Menubar.js';


class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      datamodel: {}, reports: [], report: null, search_string: '', report_date_string: '',
      nr_measurements: 0, nr_new_measurements: 0, loading: true
    };
    this.handleSearchChange = this.handleSearchChange.bind(this);
  }

  componentDidMount() {
    this.reload();
  }

  reload(event) {
    if (event) { event.preventDefault(); }
    const report_date = this.report_date() || new Date();
    fetch(`http://localhost:8080/datamodel?report_date=${report_date.toISOString()}`)
      .then(function (response) {
        return response.json();
      })
      .then(function (json) {
        self.setState({ datamodel: json });
      });
    const report_uuid = this.state.report ? this.state.report["report_uuid"] : null;
    let self = this;
    fetch(`http://localhost:8080/reports?report_date=${report_date.toISOString()}`)
      .then(function (response) {
        return response.json();
      })
      .then(function (json) {
        const nr_measurements = self.state.nr_measurements + self.state.nr_new_measurements;
        var report = null;
        if (report_uuid != null) {
          const reports = json.reports.filter((report) => report.report_uuid === report_uuid);
          if (reports.length === 1) {
            report = reports[0];
          }
        }
        self.setState(
          {
            reports: json.reports,
            report: report,
            nr_measurements: nr_measurements,
            nr_new_measurements: 0,
            loading: false
          }
        );
      });
  }

  handleSearchChange(event) {
    this.setState({ search_string: event.target.value });
  }

  handleDateChange(event, { name, value }) {
    if (this.state.hasOwnProperty(name)) {
      this.setState({ [name]: value }, () => this.reload())
    }
  }

  go_home(event) {
    event.preventDefault();
    this.setState({ report: null });
    if (this.source) {
      this.source.close()
    }
  }

  open_report(event, report) {
    event.preventDefault();
    this.setState({ report: report }, () => this.reload());
    this.source = new EventSource(`http://localhost:8080/nr_measurements/${report.report_uuid}`);
    let self = this;
    this.source.addEventListener('init', function (e) {
      self.setState({ nr_measurements: Number(e.data), nr_new_measurements: 0 });
    }, false);
    this.source.addEventListener('delta', function (e) {
      self.setState({ nr_new_measurements: Number(e.data) - self.state.nr_measurements });
    }, false);
    this.source.addEventListener('error', function (e) {
      if (e.readyState === EventSource.CLOSED) {
        self.setState({ nr_measurements: 0, nr_new_measurements: 0 });
      }
      else if (e.readyState === EventSource.OPEN) {
        self.setState({ nr_measurements: 0, nr_new_measurements: 0 });
      }
    }, false);
  }
  report_date() {
    let report_date = null;
    if (this.state.report_date_string) {
      report_date = new Date(this.state.report_date_string.split("-").reverse().join("-"));
      report_date.setHours(23, 59, 59);
    }
    return report_date;
  }

  render() {
    const report_date = this.report_date();
    return (
      <>
        <Menubar onSearch={(e) => this.handleSearchChange(e)}
          onDate={(e, { name, value }) => this.handleDateChange(e, { name, value })}
          reload={(e) => this.reload(e)} go_home={(e) => this.go_home(e)}
          nr_new_measurements={this.state.nr_new_measurements}
          report={this.state.report} report_date={report_date}
          report_date_string={this.state.report_date_string} />
        <Container fluid style={{ marginTop: '7em', paddingLeft: '1em', paddingRight: '1em' }}>
          {this.state.loading ?
            <Dimmer active inverted>
              <Loader size='large'>Loading</Loader>
            </Dimmer>
            :
            this.state.report === null ?
              <Reports reports={this.state.reports} reload={(e) => this.reload(e)}
                open_report={(e, r) => this.open_report(e, r)} />
              :
              <Report datamodel={this.state.datamodel} report={this.state.report}
                nr_new_measurements={this.state.nr_new_measurements} reload={() => this.reload()}
                search_string={this.state.search_string} report_date={report_date} />
          }
        </Container>
      </>
    );
  }
}

export default App;
