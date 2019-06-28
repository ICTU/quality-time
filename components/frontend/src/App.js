import React, { Component } from 'react';
import { Container, Segment } from 'semantic-ui-react';
import { Report } from './report/Report.js';
import { Reports } from './report/Reports.js';
import { Menubar } from './header_footer/Menubar';
import { Footer } from './header_footer/Footer';
import { createBrowserHistory } from 'history';
import { login, logout } from './api/auth';
import { get_datamodel } from './api/datamodel';
import { get_reports, get_tag_report } from './api/report';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      datamodel: {}, reports: [], report_uuid: '', search_string: '', report_date_string: '', reports_overview: {},
      nr_measurements: 0, nr_new_measurements: 0, loading: true, user: null, last_update: new Date(), login_error: false
    };
    if (window.location.hostname === "localhost") {
      window.server_url = "http://localhost:8080"
    } else {
      const domain = window.location.hostname.slice("www.".length);
      window.server_url = `http://server.${domain}:8080`
    }
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
    const pathname = this.history.location.pathname;
    const report_uuid = pathname.slice(1, pathname.length);
    this.setState({ report_uuid: report_uuid, user: localStorage.getItem("user") }, () => this.reload());
  }

  reload() {
    const report_date = this.report_date() || new Date(3000, 1, 1);
    const current_date = new Date()
    let self = this;
    get_datamodel(report_date)
      .then(function (json) {
        self.setState({ datamodel: json });
      });
    if (this.state.report_uuid.slice(0, 4) === "tag-") {
      this.setState({loading: true});
      const tag = this.state.report_uuid.slice(4);
      get_tag_report(tag, report_date)
        .then(function(json) {
          self.setState(
            {
              reports: [json],
              loading: false,
              last_update: current_date
            }
          );
        })
    } else {
      get_reports(report_date)
        .then(function (json) {
          const nr_measurements = self.state.nr_measurements + self.state.nr_new_measurements;
          self.setState(
            {
              reports: json.reports,
              reports_overview: { title: json.title, subtitle: json.subtitle },
              nr_measurements: nr_measurements,
              nr_new_measurements: 0,
              loading: false,
              last_update: current_date
            }
          );
        });
    }
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

  go_home() {
    if (this.history.location.pathname !== "/") {
      this.history.push("/");
      this.setState({ report_uuid: "" }, () => this.reload());
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
      if (e.readyState === EventSource.CLOSED || e.readyState === EventSource.OPEN) {
        self.setState({ nr_measurements: 0, nr_new_measurements: 0 });
      }
    }, false);
  }

  open_tag_report(event, tag) {
    event.preventDefault();
    const report_uuid = `tag-${tag}`
    this.setState({ report_uuid: report_uuid }, () => this.reload());
    this.history.push(report_uuid);
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
          self.setState({ user: username, login_error: false })
          localStorage.setItem("user", username)
        } else {
          self.setState({ login_error: true })
        }
      })
      .catch(function (error) {
        self.setState({ login_error: true });
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
    const current_report = this.state.reports.filter((report) => report.report_uuid === this.state.report_uuid)[0] || null;
    return (
      <div style={{ display: "flex", minHeight: "100vh", flexDirection: "column" }}>
        <Menubar
          go_home={() => this.go_home()}
          login={(u, p) => this.login(u, p)}
          login_error={this.state.login_error}
          logout={(e) => this.logout(e)}
          onDate={(e, { name, value }) => this.handleDateChange(e, { name, value })}
          onSearch={(e) => this.handleSearchChange(e)}
          report_date_string={this.state.report_date_string}
          searchable={current_report !== null}
          user={this.state.user}
        />
        <Container fluid style={{ flex: 1, marginTop: '7em', paddingLeft: '1em', paddingRight: '1em' }}>
          {this.state.loading ?
            <Segment basic placeholder loading size="massive" />
            :
            this.state.report_uuid === "" ?
              <Reports reports={this.state.reports} reload={() => this.reload()} reports_overview={this.state.reports_overview}
                open_tag_report={(e, t) => this.open_tag_report(e, t)}
                open_report={(e, r) => this.open_report(e, r)} readOnly={this.state.user === null} />
              :
              <Report datamodel={this.state.datamodel} report={current_report} go_home={() => this.go_home()}
                nr_new_measurements={this.state.nr_new_measurements} reload={() => this.reload()}
                loading={this.state.loading}
                search_string={this.state.search_string} report_date={report_date} readOnly={this.state.user === null || this.state.report_uuid.slice(0, 4) === "tag-"} />
          }
        </Container>
        <Footer last_update={this.state.last_update} report={current_report} />
      </div>
    );
  }
}

export default App;
