import React, { Component } from 'react';
import { Container, Segment } from 'semantic-ui-react';
import { SemanticToastContainer, toast } from 'react-semantic-toasts';
import 'react-semantic-toasts/styles/react-semantic-alert.css';
import './App.css';

import { Report } from './report/Report.js';
import { Reports } from './report/Reports.js';
import { Menubar } from './header_footer/Menubar';
import { Footer } from './header_footer/Footer';
import { createBrowserHistory } from 'history';
import { login, logout } from './api/auth';
import { get_datamodel } from './api/datamodel';
import { get_reports, get_tag_report } from './api/report';

function show_message(title, description, type, icon) {
  toast({
    title: title,
    type: type,
    icon: icon,
    size: "large",
    description: <p>{description}</p>,
    time: 30000
  }, () => {}, () => {}, () => {});  // Event handlers are mandatory
}

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      datamodel: {}, reports: [], report_uuid: '', search_string: '', report_date_string: '', reports_overview: {},
      nr_measurements: 0, nr_new_measurements: 0, loading_report: true, loading_datamodel: true, user: null,
      last_update: new Date(), login_error: false
    };
    const hostname = window.location.hostname;
    const server = hostname.startsWith("www.") ? `server.${hostname.slice("www.".length)}` : hostname;
    window.server_url = `http://${server}:5001`

    this.history = createBrowserHistory();
    this.history.listen((location, action) => {
      if (action === "POP") {
        const pathname = this.history.location.pathname;
        const report_uuid = pathname.slice(1, pathname.length);
        this.setState({ report_uuid: report_uuid, loading_report: true, loading_datamodel: true }, () => this.reload());
      }
    });
  }

  componentDidMount() {
    const pathname = this.history.location.pathname;
    const report_uuid = pathname.slice(1, pathname.length);
    if (report_uuid !== "") {
      this.connect_to_nr_measurements_event_source(report_uuid)
    }
    this.setState(
      { report_uuid: report_uuid, loading_report: true, loading_datamodel: true, user: localStorage.getItem("user") },
      () => this.reload());
  }

  reload(json) {
    console.log("----json--->json>>", json)
    if (json && json.availability && json.availability.status_code != 200) {
      toast({
        title: 'URL connection error!',
        type: 'warning',
        //icon: 'user x',
        time: 30000,
        description: <p>{ 'HTTP code '+ json.availability.status_code + ': ' + json.availability.reason}</p>
      });
    } else if (json && json.ok) {
      toast({
          title: 'URL connection OK!',
          type: 'success',
          //icon: 'user x',
          time: 30000
      });
    }

    if (json && json.ok === false && json.reason === "invalid_session") {
      this.logout();
      show_message("Your session expired", "Please log in to renew your session", "warning", "user x");
    }
    const report_date = this.report_date() || new Date(3000, 1, 1);
    const current_date = new Date();
    let self = this;
    get_datamodel(report_date)
      .then(function (datamodel_json) {
        self.setState({ loading_datamodel: false, datamodel: datamodel_json });
      }).catch(function (error) {
        show_message(
          "Server unreachable", "Couldn't load data from the server. Please try again later.", "error",
          "exclamation triangle")
      });
    if (this.state.report_uuid.slice(0, 4) === "tag-") {
      const tag = this.state.report_uuid.slice(4);
      get_tag_report(tag, report_date)
        .then(function (tagreport_json) {
          self.setState(
            {
              reports: Object.keys(tagreport_json.subjects).length > 0 ? [tagreport_json] : [],
              loading_report: false,
              last_update: current_date
            }
          );
        })
    } else {
      get_reports(report_date)
        .then(function (report_overview_json) {
          const nr_measurements = self.state.nr_measurements + self.state.nr_new_measurements;
          self.setState(
            {
              reports: report_overview_json.reports,
              reports_overview: { title: report_overview_json.title, subtitle: report_overview_json.subtitle },
              nr_measurements: nr_measurements,
              nr_new_measurements: 0,
              loading_report: false,
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
    this.setState({ [name]: new_report_date_string, loading_datamodel: true, loading_report: true }, () => this.reload())
  }

  go_home() {
    if (this.history.location.pathname !== "/") {
      this.history.push("/");
      this.setState({ report_uuid: "", loading_report: true, loading_datamodel: true }, () => this.reload());
      if (this.source) {
        this.source.close()
      }
    }
  }

  open_report(event, report_uuid) {
    event.preventDefault();
    this.setState({ report_uuid: report_uuid, loading_report: true, loading_datamodel: true }, () => this.reload());
    this.history.push(report_uuid);
    this.connect_to_nr_measurements_event_source(report_uuid);
  }

  connect_to_nr_measurements_event_source(report_uuid) {
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
    this.setState({ report_uuid: report_uuid, loading_datamodel: true, loading_report: true }, () => this.reload());
    this.history.push(report_uuid);
    if (this.source) {
      this.source.close()
    }
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

  logout() {
    let self = this;
    logout().then(() => {
      self.setState({ user: null });
      localStorage.removeItem("user");
    })
  }

  render() {
    const report_date = this.report_date();
    const current_report = this.state.reports.filter((report) => report.report_uuid === this.state.report_uuid)[0] || null;
    const readOnly = this.state.user === null || this.state.report_date_string || this.state.report_uuid.slice(0, 4) === "tag-";
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
        <SemanticToastContainer />
        <Container fluid className="MainContainer">
          {this.state.loading_datamodel || this.state.loading_report ?
            <Segment basic placeholder loading size="massive" />
            :
            this.state.report_uuid === "" ?
              <Reports
                open_report={(e, r) => this.open_report(e, r)}
                open_tag_report={(e, t) => this.open_tag_report(e, t)}
                readOnly={readOnly}
                reload={(json) => this.reload(json)}
                report_date={report_date}
                reports={this.state.reports}
                reports_overview={this.state.reports_overview}
              />
              :
              <Report
                datamodel={this.state.datamodel}
                go_home={() => this.go_home()}
                nr_new_measurements={this.state.nr_new_measurements}
                readOnly={readOnly}
                reload={(json) => this.reload(json)}
                report={current_report}
                report_date={report_date}
                search_string={this.state.search_string}
              />
          }
        </Container>
        <Footer last_update={this.state.last_update} report={current_report} />
      </div>
    );
  }
}

export default App;
