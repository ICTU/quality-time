import React, { Component } from 'react';
import { Container, Dimmer, Loader } from 'semantic-ui-react';
import { Report } from './Report.js';
import { Reports } from './Reports.js';
import { Menubar } from './Menubar.js';
import { createBrowserHistory } from 'history';


class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      datamodel: {}, reports: [], report_uuid: '', search_string: '', report_date_string: '',
      nr_measurements: 0, nr_new_measurements: 0, loading: true, user: null
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
    const report_date = this.report_date() || new Date(3000, 12, 31);
    fetch(`${window.server_url}/datamodel?report_date=${report_date.toISOString()}`)
      .then(function (response) {
        return response.json();
      })
      .then(function (json) {
        self.setState({ datamodel: json });
      });
    let self = this;
    fetch(`${window.server_url}/reports?report_date=${report_date.toISOString()}`)
      .then(function (response) {
        return response.json();
      })
      .then(function (json) {
        const nr_measurements = self.state.nr_measurements + self.state.nr_new_measurements;
        self.setState(
          {
            reports: json.reports,
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
    fetch(`${window.server_url}/login`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({ username: username, password: password })
    })
      .then(function (response) {
        return response.json()
      })
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
    fetch(`${window.server_url}/logout`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({}),
      credentials: 'include'
    }).then(function (response) {
      self.setState({ user: null });
      localStorage.setItem("user", null);
    }).catch(function (error) {
      console.log(error);
    })
  }

  render() {
    const report_date = this.report_date();
    const report = this.state.reports.filter((report) => report.report_uuid === this.state.report_uuid)[0] || null;
    return (
      <>
        <Menubar onSearch={(e) => this.handleSearchChange(e)}
          onDate={(e, { name, value }) => this.handleDateChange(e, { name, value })}
          reload={(e) => this.reload(e)} go_home={(e) => this.go_home(e)}
          nr_new_measurements={this.state.nr_new_measurements} user={this.state.user}
          report={report} report_date={report_date} login={(u, p) => this.login(u, p)}
          logout={(e) => this.logout(e)}
          report_date_string={this.state.report_date_string} />
        <Container fluid style={{ marginTop: '7em', paddingLeft: '1em', paddingRight: '1em' }}>
          {this.state.loading ?
            <Dimmer active inverted>
              <Loader size='large'>Loading</Loader>
            </Dimmer>
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
      </>
    );
  }
}

export default App;
