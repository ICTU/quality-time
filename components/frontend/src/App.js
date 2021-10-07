import React, { Component } from 'react';
import { Container, Segment } from 'semantic-ui-react';
import { ToastContainer } from 'react-toastify';
import HashLinkObserver from "react-hash-link";
import { createBrowserHistory, Action } from 'history';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';

import { Report } from './report/Report.js';
import { ReportsOverview } from './report/ReportsOverview.js';
import { Menubar } from './header_footer/Menubar';
import { Footer } from './header_footer/Footer';
import { parse, stringify } from 'query-string';

import { Permissions } from './context/Permissions';
import { get_datamodel } from './api/datamodel';
import { get_reports, get_reports_overview } from './api/report';
import { nr_measurements_api } from './api/measurement';
import { login } from './api/auth';
import { show_message, show_connection_messages } from './widgets/toast';
import { getUserPermissions, isValidDate_YYYYMMDD } from './utils'
import { DataModel } from './context/Contexts';

class App extends Component {
    constructor(props) {
        super(props);
        this.state = {
            datamodel: {}, reports: [], report_uuid: '', report_date_string: '', reports_overview: {},
            nr_measurements: 0, loading: true, user: null, email: null, last_update: new Date()
        };
        this.history = createBrowserHistory();
        this.history.listen(({ location, action }) => this.on_history({ location, action }));
    }

    on_history({ location, action }) {
        if (action === Action.Pop) {
            const pathname = location.pathname;
            const report_uuid = pathname.slice(1, pathname.length);
            this.setState({ report_uuid: report_uuid, loading: true }, () => this.reload());
        }
    }

    componentDidMount() {
        const pathname = this.history.location.pathname;
        const report_uuid = pathname.slice(1, pathname.length);
        const report_date_iso_string = parse(this.history.location.search).report_date || "";
        const report_date_string = isValidDate_YYYYMMDD(report_date_iso_string) ? report_date_iso_string.split("-").reverse().join("-") : "";
        this.login_forwardauth();
        this.connect_to_nr_measurements_event_source();
        if (new Date(localStorage.getItem("session_expiration_datetime")) < new Date()) {
            this.set_user(null)  // The session expired while the user was away
        }
        this.setState(
            {
                report_uuid: report_uuid, report_date_string: report_date_string, loading: true,
                user: localStorage.getItem("user"), email: localStorage.getItem("email")
            },
            () => this.reload());
    }

    componentWillUnmount() {
        this.source.close();
    }

    reload(json) {
        if (json) {
            show_connection_messages(json);
            this.changed_fields = json.availability ? json.availability.filter((url_key) => url_key.status_code !== 200) : null;
            this.check_session(json)
        }
        const report_date = this.report_date();
        const show_error = () => show_message("error", "Server unreachable", "Couldn't load data from the server. Please try again later.");
        this.loadAndSetState(report_date, show_error)
    }

    loadAndSetState(report_date, show_error) {
        Promise.all([get_datamodel(report_date), get_reports_overview(report_date), get_reports(this.state.report_uuid, report_date)]).then(
            ([data_model, reports_overview, reports]) => {
                if (data_model.ok === false || reports.ok === false) {
                    show_error();
                } else {
                    const now = new Date();
                    this.setState({
                        loading: false,
                        datamodel: data_model,
                        reports_overview: {
                            layout: reports_overview.layout,
                            subtitle: reports_overview.subtitle,
                            title: reports_overview.title,
                            permissions: reports_overview.permissions
                        },
                        reports: reports.reports || [],
                        last_update: now
                    });
                }
            }).catch(show_error);
    }

    check_session(json) {
        if (json.ok === false && json.status === 401) {
            this.set_user(null);
            if (this.login_forwardauth() === false) {
                show_message("warning", "Your session expired", "Please log in to renew your session");
            }
        }
    }

    handleDateChange(event, { name, value }) {
        const today = new Date();
        const today_string = String(today.getDate()).padStart(2, '0') + '-' + String(today.getMonth() + 1).padStart(2, '0') + '-' + today.getFullYear();
        const new_report_date_string = value === today_string ? '' : value;
        let parsed = parse(this.history.location.search);
        parsed.report_date = new_report_date_string.split("-").reverse().join("-");
        const search = stringify(parsed, { skipEmptyString: true });
        this.history.replace({ search: search.length > 0 ? "?" + search : "" })
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

    report_date() {
        let report_date = null;
        if (this.state.report_date_string) {
            report_date = new Date(this.state.report_date_string.split("-").reverse().join("-"));
            report_date.setHours(23, 59, 59);
        }
        return report_date;
    }

    current_report_is_tag_report() {
        return this.state.report_uuid.slice(0, 4) === "tag-"
    }

    login_forwardauth() {
        let self = this;
        login("", "")
            .then(function (json) {
                if (json.ok) {
                    self.set_user(json.email, json.email, json.session_expiration_datetime);
                    return true;
                }
            });
        return false;
    }

    set_user(username, email, session_expiration_datetime) {
        const email_address = email && email.indexOf("@") > -1 ? email : null;
        this.setState({ user: username, email: email_address });
        if (username === null) {
            localStorage.removeItem("user");
            localStorage.removeItem("email");
            localStorage.removeItem("session_expiration_datetime");
        } else {
            localStorage.setItem("user", username);
            localStorage.setItem("email", email_address);
            localStorage.setItem("session_expiration_datetime", session_expiration_datetime.toISOString());
        }
    }

    render() {
        const report_date = this.report_date();
        const current_report = this.state.reports.filter((report) => report.report_uuid === this.state.report_uuid)[0] || null;
        const permissions = this.state.reports_overview.permissions || {};
        const user_permissions = getUserPermissions(this.state.user, this.state.email, this.current_report_is_tag_report(), report_date, permissions)
        return (
            <div style={{ display: "flex", minHeight: "100vh", flexDirection: "column" }}>
                <HashLinkObserver />
                <Menubar
                    email={this.state.email}
                    go_home={() => this.go_home()}
                    onDate={(e, { name, value }) => this.handleDateChange(e, { name, value })}
                    report_date_string={this.state.report_date_string}
                    set_user={(username, email, session_expiration_datetime) => this.set_user(username, email, session_expiration_datetime)}
                    user={this.state.user}
                />
                <ToastContainer theme="colored" />
                <Permissions.Provider value={user_permissions}>
                    <DataModel.Provider value={this.state.datamodel}>
                      <Container fluid className="MainContainer">
                          {this.state.loading ?
                              <Segment basic placeholder loading size="massive" />
                              :
                              this.state.report_uuid === "" ?
                                  <ReportsOverview
                                      reports={this.state.reports}
                                      open_report={(e, r) => this.open_report(e, r)}
                                      report_date={report_date}
                                      reports_overview={this.state.reports_overview}
                                      reload={(json) => this.reload(json)}
                                  />
                                  :
                                  <Report
                                      go_home={() => this.go_home()}
                                      nr_measurements={this.state.nr_measurements}
                                      report={current_report}
                                      changed_fields={this.changed_fields}
                                      reload={(json) => this.reload(json)}
                                      report_date={report_date}
                                      reports={this.state.reports}
                                      history={this.history}
                                  />
                          }
                      </Container>
                    </DataModel.Provider>
                </Permissions.Provider>
                <Footer last_update={this.state.last_update} report={current_report} />
            </div>
        );
    }
}

export default App;
