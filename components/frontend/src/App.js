import React, { Component } from 'react';
import { Container, Segment } from 'semantic-ui-react';
import { Report } from './report/Report.js';
import { Reports } from './report/Reports.js';
import { Menubar } from './header_footer/Menubar';
import { Footer } from './header_footer/Footer';
import { createBrowserHistory } from 'history';
import { login, logout } from './api/auth';
import { get_datamodel } from './api/datamodel';
import { get_reports } from './api/report';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      datamodel: {}, reports: [], report_uuid: '', search_string: '', report_date_string: '',
      nr_measurements: 0, nr_new_measurements: 0, loading: true, user: null, last_update: new Date()
    };
    this.handleSearchChange = this.handleSearchChange.bind(this);
    window.server_url = process.env.REACT_APP_SERVER_URL || "http://localhost:8080";
    this.history = createBrowserHistory();
    this.history.listen((location, action) => {
      if (action === "POP") {
        const pathname = this.history.location.pathname;
        const report_uuid = pathname.slice(1, pathname.length);
        this.setState({ report_uuid: report_uuid }, () => this.reload());
      }
    });
  }

  componentDidMount() {
    this.reload();
    const pathname = this.history.location.pathname;
    const report_uuid = pathname.slice(1, pathname.length);
    this.setState({ report_uuid: report_uuid, user: localStorage.getItem("user") });
  }

  reload(event) {
    if (event) { event.preventDefault(); }
    const report_date = this.report_date() || new Date(3000, 1, 1);
    let self = this;
    get_datamodel(report_date)
      .then(function (json) {
        self.setState({ datamodel: json });
      });
    get_reports(report_date)
      .then(function (json) {
        const nr_measurements = self.state.nr_measurements + self.state.nr_new_measurements;
        const current_date = new Date()
        self.setState(
          {
            reports: json.reports,
            nr_measurements: nr_measurements,
            nr_new_measurements: 0,
            loading: false,
            last_update: current_date
          }
        );
      });
  }

  handleSearchChange(event) {
    this.setState({ search_string: event.target.value });
  }

  handleDateChange(event, { name, value }) {
    const today = new Date();
    const today_string = String(today.getDate()).padStart(2, '0') + '-' + String(today.getMonth() + 1).padStart(2, '0') + '-' + today.getFullYear();
    const new_report_date_string = value === today_string ? '' : value;
    this.setState({ [name]: new_report_date_string }, () => this.reload())
  }

  go_home(event) {
    this.reload(event);
    if (this.history.location.pathname !== "/") {
      this.history.push("/");
      this.setState({ report_uuid: "" });
      if (this.source) {
        this.source.close()
      }
    }
  }

  open_report(event, report_uuid) {
    event.preventDefault();
    this.setState({ report_uuid: report_uuid }, () => this.reload());
    this.history.push(report_uuid);
    this.source = new EventSource(`${window.server_url}/nr_measurements/${report_uuid}`);
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

  login(username, password) {
    let self = this;
    login(username, password)
      .then(function (json) {
        if (json.ok) {
          self.setState({ user: username })
          localStorage.setItem("user", username)
        }
      })
      .catch(function (error) {
        console.log(error);
      });
  }

  logout(event) {
    event.preventDefault();
    let self = this;
    logout().then(() => {
      self.setState({ user: null });
      localStorage.setItem("user", null);
    })
  }

  render() {
    const report_date = this.report_date();
    const report = this.state.reports.filter((report) => report.report_uuid === this.state.report_uuid)[0] || null;
    return (
      <div style={{ display: "flex", minHeight: "100vh", flexDirection: "column" }}>
        <Menubar onSearch={(e) => this.handleSearchChange(e)}
          onDate={(e, { name, value }) => this.handleDateChange(e, { name, value })}
          go_home={(e) => this.go_home(e)} user={this.state.user}
          report_date={report_date} login={(u, p) => this.login(u, p)}
          logout={(e) => this.logout(e)}
          report_date_string={this.state.report_date_string} />
        <Container fluid style={{ flex: 1, marginTop: '7em', paddingLeft: '1em', paddingRight: '1em' }}>
          {this.state.loading ?
            <Segment basic placeholder loading size="massive" />
            :
            this.state.report_uuid === "" ?
              <Reports reports={this.state.reports} reload={(e) => this.reload(e)}
                open_report={(e, r) => this.open_report(e, r)} readOnly={this.state.user === null} />
              :
              <Report datamodel={this.state.datamodel} report={report} go_home={(e) => this.go_home(e)}
                nr_new_measurements={this.state.nr_new_measurements} reload={() => this.reload()}
                search_string={this.state.search_string} report_date={report_date} readOnly={this.state.user === null} />
          }
        </Container>
        <Footer last_update={this.state.last_update} report={report} />
      </div>
    );
  }
}

export default App;
