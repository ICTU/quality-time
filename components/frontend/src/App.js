import React, { Component } from 'react';
import { Container, Segment } from 'semantic-ui-react';
import { SemanticToastContainer, toast } from 'react-semantic-toasts';
import HashLinkObserver from "react-hash-link";
import 'react-semantic-toasts/styles/react-semantic-alert.css';
import './App.css';

import { Report } from './report/Report.js';
import { Reports } from './report/Reports.js';
import { Menubar } from './header_footer/Menubar';
import { Footer } from './header_footer/Footer';
import { createBrowserHistory } from 'history';
import { ReadOnlyContext } from './context/ReadOnly';
import { login, logout } from './api/auth';
import { get_datamodel } from './api/datamodel';
import { get_reports, get_tag_report } from './api/report';
import { nr_measurements_api } from './api/measurement';

function show_message(type, title, description, icon) {
  toast({
    title: title,
    type: type,
    icon: icon,
    size: "large",
    description: <p>{description}</p>,
    time: 30000
  }, () => { }, () => { }, () => { });  // Event handlers are mandatory
}

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      datamodel: {}, reports: [], report_uuid: '', search_string: '', report_date_string: '', reports_overview: {},
      nr_measurements: 0, loading: true, user: null, email: null, last_update: new Date(), login_error: false
    };
    this.history = createBrowserHistory();
    this.history.listen((location, action) => {
      if (action === "POP") {
        const pathname = this.history.location.pathname;
        const report_uuid = pathname.slice(1, pathname.length);
        this.setState({ report_uuid: report_uuid, loading: true }, () => this.reload());
      }
    });
  }

  componentDidMount() {
    const pathname = this.history.location.pathname;
    const report_uuid = pathname.slice(1, pathname.length);
    this.connect_to_nr_measurements_event_source()
    this.setState(
      { report_uuid: report_uuid, loading: true, user: localStorage.getItem("user"), email: localStorage.getItem("email") },
      () => this.reload());
  }

  componentWillUnmount() {
    this.source.close();
  }

  reload(json) {
    if (json) {
      this.show_connection_messages(json);
      this.check_session(json)
    }
    const report_date = this.report_date() || new Date(3000, 1, 1);
    const now = new Date();
    const show_error = () => show_message("error", "Server unreachable", "Couldn't load data from the server. Please try again later.");
    if (this.state.report_uuid.slice(0, 4) === "tag-") {
      const tag = this.state.report_uuid.slice(4);
      Promise.all([get_datamodel(report_date), get_tag_report(tag, report_date)]).then(
        ([data_model, report]) => {
          if (data_model.ok === false || report.ok === false) {
            show_error();
          } else {
            this.setState({
              loading: false,
              datamodel: data_model,
              reports: Object.keys(report.subjects).length > 0 ? [report] : [],
              last_update: now
            })
          }
        }).catch(show_error);
    } else {
      Promise.all([get_datamodel(report_date), get_reports(report_date)]).then(
        ([data_model, reports]) => {
          if (data_model.ok === false || reports.ok === false) {
            show_error();
          } else {
            this.setState({
              loading: false,
              datamodel: data_model,
              reports: reports.reports || [],
              reports_overview: { layout: reports.layout, subtitle: reports.subtitle, title: reports.title },
              last_update: now
            })
          }
        }).catch(show_error);
    }
  }

  show_connection_messages(json) {
    this.changed_fields = null
    if (json.availability) {
      this.changed_fields = json.availability.filter((url_key) => url_key.status_code !== 200)
      json.availability.map((url_key) => {
        if (url_key.status_code === 200) {
          show_message("success", "URL connection OK")
        } else {
          show_message("warning", "URL connection error", "HTTP code " + url_key.status_code + ": " + url_key.reason)
        }
        return null
      })
    }
  }

  check_session(json) {
    if (json.ok === false && json.status === 401) {
      this.logout();
      show_message("warning", "Your session expired", "Please log in to renew your session", "user x");
    }
  }

  handleSearchChange(event) {
    this.setState({ search_string: event.target.value });
  }

  handleDateChange(event, { name, value }) {
    const today = new Date();
    const today_string = String(today.getDate()).padStart(2, '0') + '-' + String(today.getMonth() + 1).padStart(2, '0') + '-' + today.getFullYear();
    const new_report_date_string = value === today_string ? '' : value;
    this.setState({ [name]: new_report_date_string, loading: true }, () => this.reload())
  }

  go_home() {
    if (this.history.location.pathname !== "/") {
      this.history.push("/");
      this.setState({ report_uuid: "", loading: true }, () => this.reload());
    }
  }

  open_report(event, report_uuid) {
    event.preventDefault();
    this.setState({ report_uuid: report_uuid, loading: true }, () => this.reload());
    this.history.push(report_uuid);
  }

  connect_to_nr_measurements_event_source() {
    this.source = new EventSource(nr_measurements_api);
    let self = this;
    this.source.addEventListener('init', function (e) {
      self.setState({ nr_measurements: Number(e.data) });
    }, false);
    this.source.addEventListener('delta', function (e) {
      self.setState({ nr_measurements: Number(e.data) }, () => self.reload());
    }, false);
    this.source.addEventListener('error', function (e) {
      if (e.readyState === EventSource.CLOSED || e.readyState === EventSource.OPEN) {
        self.setState({ nr_measurements: 0 });
      }
    }, false);
  }

  open_tag_report(event, tag) {
    event.preventDefault();
    const report_uuid = `tag-${tag}`
    this.setState({ report_uuid: report_uuid, loading: true }, () => this.reload());
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
          const email = json.email.indexOf("@") > -1 ? json.email : null;
          self.setState({ user: username, email: email, login_error: false })
          localStorage.setItem("user", username)
          localStorage.setItem("email", email)
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
      localStorage.removeItem("email");
    })
  }

  render() {
    const report_date = this.report_date();
    const current_report = this.state.reports.filter((report) => report.report_uuid === this.state.report_uuid)[0] || null;
    const readOnly = this.state.user === null || this.state.report_date_string || this.state.report_uuid.slice(0, 4) === "tag-";
    const props = { reload: (json) => this.reload(json), report_date: report_date, reports: this.state.reports };
    return (
      <div style={{ display: "flex", minHeight: "100vh", flexDirection: "column" }}>
        <HashLinkObserver />
        <Menubar
          email={this.state.email}
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
        <ReadOnlyContext.Provider value={readOnly}>
          <Container fluid className="MainContainer">
            {this.state.loading ?
              <Segment basic placeholder loading size="massive" />
              :
              this.state.report_uuid === "" ?
                <Reports
                  open_report={(e, r) => this.open_report(e, r)}
                  open_tag_report={(e, t) => this.open_tag_report(e, t)}
                  reports_overview={this.state.reports_overview}
                  {...props}
                />
                :
                <Report
                  datamodel={this.state.datamodel}
                  go_home={() => this.go_home()}
                  nr_measurements={this.state.nr_measurements}
                  report={current_report}
                  search_string={this.state.search_string}
                  changed_fields={this.changed_fields}
                  {...props}
                />
            }
          </Container>
        </ReadOnlyContext.Provider>
        <Footer last_update={this.state.last_update} report={current_report} />
      </div>
    );
  }
}

export default App;
