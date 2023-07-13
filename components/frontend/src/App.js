import React, { Component } from 'react';
import history from 'history/browser';
import { Action } from 'history';
import { get_datamodel } from './api/datamodel';
import { get_report, get_reports_overview } from './api/report';
import { nr_measurements_api } from './api/measurement';
import { login } from './api/auth';
import { showMessage, showConnectionMessage } from './widgets/toast';
import { isValidDate_YYYYMMDD, registeredURLSearchParams, reportIsTagReport, toISODateStringInCurrentTZ } from './utils'
import { AppUI } from './AppUI';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';

class App extends Component {
    constructor(props) {
        super(props);
        this.state = {
            datamodel: {},
            reports: [],
            report_uuid: '',
            report_date: null,
            reports_overview: {},
            nrMeasurements: 0,
            nrMeasurementsStreamConnected: true,  // Assume initial connection will be successful
            loading: true,
            user: null,
            email: null,
            last_update: new Date()
        };
        history.listen(({ location, action }) => this.on_history({ location, action }));
    }

    on_history({ location, action }) {
        if (action === Action.Pop) {
            const pathname = location.pathname;
            const report_uuid = pathname.slice(1, pathname.length);
            this.setState({ report_uuid: report_uuid, loading: true }, () => this.reload());
        }
    }

    componentDidMount() {
        const pathname = history.location.pathname;
        const report_uuid = decodeURI(pathname.slice(1, pathname.length));
        const report_date_iso_string = registeredURLSearchParams().get("report_date") || "";
        let reportDate = null;
        if (isValidDate_YYYYMMDD(report_date_iso_string)) {
            reportDate = new Date(report_date_iso_string);
            reportDate.setHours(23, 59, 59);
        }
        this.login_forwardauth();
        this.initUserSession()
        this.connectToNrMeasurementsEventSource();
        this.setState({ report_uuid: report_uuid, report_date: reportDate, loading: true }, () => this.reload());
    }

    componentWillUnmount() {
        this.source.close();
    }

    reload(json) {
        if (json) {
            showConnectionMessage(json);
            this.changed_fields = json.availability ? json.availability.filter((url_key) => url_key.status_code !== 200) : null;
            this.check_session(json)
        }
        const show_error = () => showMessage("error", "Server unreachable", "Couldn't load data from the server.");
        this.loadAndSetState(show_error)
    }

    loadAndSetState(show_error) {
        const report_uuid = this.state.report_uuid;
        const reportDate = this.state.report_date
        Promise.all([get_datamodel(reportDate), get_reports_overview(reportDate), get_report(report_uuid, reportDate)]).then(
            ([data_model, reports_overview, reports]) => {
                if (this.state.report_uuid !== report_uuid) {
                    return  // User navigated to a different report or to the overview page, cancel update
                }
                if (data_model.ok === false || reports.ok === false) {
                    show_error();
                } else {
                    const now = new Date();
                    this.setState({
                        loading: false,
                        datamodel: data_model,
                        reports_overview: reports_overview,
                        reports: reports.reports || [],
                        last_update: now
                    });
                }
            }).catch(show_error);
    }

    check_session(json) {
        if (json.ok === false && json.status === 401) {
            this.setUserSession();
            if (this.login_forwardauth() === false) {
                showMessage("warning", "Your session expired", "Please log in to renew your session");
            }
        }
    }

    handleDateChange(date) {
        let parsed = registeredURLSearchParams();
        if (date && toISODateStringInCurrentTZ(date) < toISODateStringInCurrentTZ(new Date())) {
            // We're time traveling, set the report_date query parameter
            parsed.set("report_date", toISODateStringInCurrentTZ(date));
            if (!this.state.report_date) {
                // We're time traveling from the present, warn the user
                showMessage(
                    "info",
                    "Historic information is read-only",
                    "You are viewing historic information. Editing is not possible."
                )
            }
        } else {
            // We're (back) in the present
            parsed.delete("report_date")
            date = null
        }
        const search = parsed.toString().replace(/%2C/g, ",")  // No need to encode commas
        history.replace({ search: search.length > 0 ? "?" + search : "" })
        this.setState({ report_date: date, loading: true }, () => this.reload())
    }

    go_home() {
        if (history.location.pathname !== "/") {
            this.history_push("/")
            this.setState({ report_uuid: "", loading: true }, () => this.reload());
        }
    }

    open_report(event, report_uuid) {
        event.preventDefault();
        this.history_push(encodeURI(report_uuid))
        if (reportIsTagReport(report_uuid)) {
            showMessage(
                "info",
                "Tag reports are read-only",
                "You opened a report for a specific metric tag. These reports are generated dynamically. Editing is not possible."
            )
        }
        this.setState({ report_uuid: report_uuid, loading: true }, () => this.reload());
    }

    history_push(target) {
        const search = registeredURLSearchParams().toString().replace(/%2C/g, ",")  // No need to encode commas
        history.push(target + (search.length > 0 ? "?" + search : ""));
    }

    connectToNrMeasurementsEventSource() {
        this.source = new EventSource(nr_measurements_api);
        let self = this;
        this.source.addEventListener("init", (message) => {
            const newNrMeasurements = Number(message.data);
            if (!self.state.nrMeasurementsStreamConnected) {
                showMessage("success", "Connected to server", "Successfully reconnected to server.")
                self.setState({ nrMeasurements: newNrMeasurements, nrMeasurementsStreamConnected: true }, () => self.reload());
            } else {
                self.setState({ nrMeasurements: newNrMeasurements });
            }
        });
        this.source.addEventListener("delta", (message) => {
            const newNrMeasurements = Number(message.data);
            if (newNrMeasurements !== self.state.nrMeasurements) {
                self.setState({ nrMeasurements: newNrMeasurements }, () => self.reload());
            }
        });
        this.source.addEventListener("error", () => {
            showMessage("error", "Server unreachable", "Trying to reconnect to server...")
            self.setState({ nrMeasurementsStreamConnected: false })
        });
    }

    login_forwardauth() {
        let self = this;
        login("", "")
            .then(function (json) {
                if (json.ok) {
                    self.setUserSession(json.email, json.email, new Date(json.session_expiration_datetime));
                    return true;
                }
            });
        return false;
    }

    initUserSession() {
        // Check if there is a session expiration datetime in the local storage. If so, restore the session as long as
        // it has not expired. Otherwise, nothing needs to be done.
        const sessionExpirationDateTimeISOString = localStorage.getItem("session_expiration_datetime")
        if (sessionExpirationDateTimeISOString) {
            const sessionExpirationDateTime = new Date(sessionExpirationDateTimeISOString)
            if (sessionExpirationDateTime < new Date()) {
                // The session expired while the user was away. Reset it and notify the user of the expired session.
                this.onUserSessionExpiration()
            } else {
                // Session is still active, restore it from local storage.
                this.setUserSession(localStorage.getItem("user"), localStorage.getItem("email"), sessionExpirationDateTime)
            }
        } else {
            showMessage(
                "info",
                "Not logged in",
                "You are not logged in. Editing is not possible until you are."
            )
        }
    }

    setUserSession(username, email, sessionExpirationDateTime) {
        if (username) {
            const emailAddress = email && email.indexOf("@") > -1 ? email : null;
            this.setState({ user: username, email: emailAddress });
            localStorage.setItem("user", username);
            localStorage.setItem("email", emailAddress);
            localStorage.setItem("session_expiration_datetime", sessionExpirationDateTime.toISOString());
            this.sessionExpirationTimeoutId = setTimeout(
                () => this.onUserSessionExpiration(), sessionExpirationDateTime - new Date()
            )
        } else {
            this.setState({ user: null, email: null });
            localStorage.removeItem("user");
            localStorage.removeItem("email");
            localStorage.removeItem("session_expiration_datetime");
            clearTimeout(this.sessionExpirationTimeoutId)
        }
    }

    onUserSessionExpiration() {
        this.setUserSession();
        showMessage("warning", "Your session expired", "Please log in to renew your session.");
    }

    render() {
        return (
            <AppUI
                changed_fields={this.changed_fields}
                datamodel={this.state.datamodel}
                email={this.state.email}
                go_home={() => this.go_home()}
                handleDateChange={(date) => this.handleDateChange(date)}
                last_update={this.state.last_update}
                loading={this.state.loading}
                nrMeasurements={this.state.nrMeasurements}
                open_report={(e, r) => this.open_report(e, r)}
                reload={(json) => this.reload(json)}
                report_date={this.state.report_date}
                report_uuid={this.state.report_uuid}
                reports={this.state.reports}
                reports_overview={this.state.reports_overview}
                set_user={(username, email, sessionExpirationDateTime) => this.setUserSession(username, email, sessionExpirationDateTime)}
                user={this.state.user}
            />
        );
    }
}

export default App;
