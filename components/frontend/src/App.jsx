import "./App.css"

import { CssBaseline } from "@mui/material"
import { ThemeProvider } from "@mui/material/styles"
import { Action } from "history"
import history from "history/browser"
import { Component } from "react"

import { login } from "./api/auth"
import { getDataModel } from "./api/datamodel"
import { nrMeasurementsApi } from "./api/measurement"
import { getReport, getReportsOverview } from "./api/report"
import { AppUI } from "./AppUI"
import { registeredURLSearchParams } from "./hooks/url_search_query"
import { theme } from "./theme"
import { isValidISODate, toISODateStringInCurrentTZ } from "./utils"
import { showConnectionMessage, showMessage } from "./widgets/toast"

class App extends Component {
    constructor(props) {
        super(props)
        this.state = {
            dataModel: {},
            lastUpdate: new Date(),
            reports: [],
            reportDate: null,
            reportUuid: "",
            reportsOverview: {},
            nrMeasurements: 0,
            nrMeasurementsStreamConnected: true, // Assume initial connection will be successful
            loading: true,
            user: null,
            email: null,
        }
        history.listen(({ location, action }) => this.onHistory({ location, action }))
    }

    onHistory({ location, action }) {
        if (action === Action.Pop) {
            const pathname = location.pathname
            const reportUuid = pathname.slice(1, pathname.length)
            this.setState({ reportUuid: reportUuid, loading: true }, () => this.reload())
        }
    }

    componentDidMount() {
        const pathname = history.location.pathname
        const reportUuid = decodeURI(pathname.slice(1, pathname.length))
        const reportDateISOString = registeredURLSearchParams().get("report_date") || ""
        let reportDate = null
        if (isValidISODate(reportDateISOString)) {
            reportDate = new Date(reportDateISOString)
            reportDate.setHours(23, 59, 59)
        }
        this.loginForwardAuth()
        this.initUserSession()
        this.connectToNrMeasurementsEventSource()
        this.setState({ reportUuid: reportUuid, reportDate: reportDate, loading: true }, () => this.reload())
    }

    componentWillUnmount() {
        this.source.close()
    }

    reload(json) {
        if (json) {
            showConnectionMessage(json)
            this.changedFields = json.availability
                ? json.availability.filter((urlKey) => urlKey.status_code !== 200)
                : null
            this.checkSession(json)
        }
        const showError = () => showMessage("error", "Server unreachable", "Couldn't load data from the server.")
        this.loadAndSetState(showError)
    }

    loadAndSetState(showError) {
        const reportUuid = this.state.reportUuid
        const reportDate = this.state.reportDate
        Promise.all([getDataModel(reportDate), getReportsOverview(reportDate), getReport(reportUuid, reportDate)])
            .then(([dataModel, reportsOverview, reports]) => {
                if (this.state.reportUuid !== reportUuid) {
                    return // User navigated to a different report or to the overview page, cancel update
                }
                if (dataModel.ok === false || reports.ok === false) {
                    showError()
                } else {
                    const now = new Date()
                    this.setState({
                        dataModel: dataModel,
                        lastUpdate: now,
                        loading: false,
                        reports: reports.reports || [],
                        reportsOverview: reportsOverview,
                    })
                }
                return null
            })
            .catch(showError)
    }

    checkSession(json) {
        if (json.ok === false && json.status === 401) {
            this.setUserSession()
            if (this.loginForwardAuth() === false) {
                showMessage("warning", "Your session expired", "Please log in to renew your session")
            }
        }
    }

    handleDateChange(date) {
        let parsed = registeredURLSearchParams()
        if (date && toISODateStringInCurrentTZ(date) < toISODateStringInCurrentTZ(new Date())) {
            // We're time traveling, set the report_date query parameter
            parsed.set("report_date", toISODateStringInCurrentTZ(date))
            const now = new Date()
            date.setHours(now.getHours(), now.getMinutes())
            if (!this.state.reportDate) {
                // We're time traveling from the present, warn the user
                showMessage(
                    "info",
                    "Historic information is read-only",
                    "You are viewing historic information. Editing is not possible.",
                )
            }
        } else {
            // We're (back) in the present
            parsed.delete("report_date")
            date = null
        }
        const search = parsed.toString().replaceAll("%2C", ",") // No need to encode commas
        history.replace({ search: search.length > 0 ? "?" + search : "" })
        this.setState({ reportDate: date, loading: true }, () => this.reload())
    }

    openReportsOverview() {
        if (history.location.pathname !== "/") {
            this.historyPush("/")
            this.setState({ reportUuid: "", loading: true }, () => this.reload())
        }
    }

    openReport(reportUuid) {
        this.historyPush(encodeURI(reportUuid))
        this.setState({ reportUuid: reportUuid, loading: true }, () => this.reload())
    }

    historyPush(target) {
        const search = registeredURLSearchParams().toString().replaceAll("%2C", ",") // No need to encode commas
        history.push(target + (search.length > 0 ? "?" + search : ""))
    }

    connectToNrMeasurementsEventSource() {
        this.source = new EventSource(nrMeasurementsApi)
        this.source.addEventListener("init", (message) => {
            const newNrMeasurements = Number(message.data)
            if (this.state.nrMeasurementsStreamConnected) {
                this.setState({ nrMeasurements: newNrMeasurements })
            } else {
                showMessage("success", "Connected to server", "Successfully reconnected to server.")
                this.setState({ nrMeasurements: newNrMeasurements, nrMeasurementsStreamConnected: true }, () =>
                    this.reload(),
                )
            }
        })
        this.source.addEventListener("delta", (message) => {
            const newNrMeasurements = Number(message.data)
            if (newNrMeasurements !== this.state.nrMeasurements) {
                this.setState({ nrMeasurements: newNrMeasurements }, () => this.reload())
            }
        })
        this.source.addEventListener("error", () => {
            showMessage("error", "Server unreachable", "Trying to reconnect to server...", "reconnecting")
            this.setState({ nrMeasurementsStreamConnected: false })
        })
    }

    loginForwardAuth() {
        login("", "")
            .then((json) => {
                if (json.ok) {
                    this.setUserSession(json.email, json.email, new Date(json.session_expiration_datetime))
                    return true
                }
                return false
            })
            .catch((error) => showMessage("error", "Login with forward authentication failed", `${error}`))
        return false
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
                this.setUserSession(
                    localStorage.getItem("user"),
                    localStorage.getItem("email"),
                    sessionExpirationDateTime,
                )
            }
        } else {
            showMessage("info", "Not logged in", "You are not logged in. Editing is not possible until you are.")
        }
    }

    setUserSession(username, email, sessionExpirationDateTime) {
        if (username) {
            const emailAddress = email?.includes("@") ? email : null
            this.setState({ user: username, email: emailAddress })
            localStorage.setItem("user", username)
            localStorage.setItem("email", emailAddress)
            localStorage.setItem("session_expiration_datetime", sessionExpirationDateTime.toISOString())
            this.sessionExpirationTimeoutId = setTimeout(
                () => this.onUserSessionExpiration(),
                sessionExpirationDateTime - Date.now(),
            )
        } else {
            this.setState({ user: null, email: null })
            localStorage.removeItem("user")
            localStorage.removeItem("email")
            localStorage.removeItem("session_expiration_datetime")
            clearTimeout(this.sessionExpirationTimeoutId)
        }
    }

    onUserSessionExpiration() {
        this.setUserSession()
        showMessage("warning", "Your session expired", "Please log in to renew your session.")
    }

    render() {
        return (
            <ThemeProvider theme={theme}>
                <CssBaseline enableColorScheme />
                <AppUI
                    changedFields={this.changedFields}
                    dataModel={this.state.dataModel}
                    email={this.state.email}
                    openReportsOverview={() => this.openReportsOverview()}
                    handleDateChange={(date) => this.handleDateChange(date)}
                    key={this.state.reportUuid} // Make sure the AppUI is refreshed whenever the current report changes
                    lastUpdate={this.state.lastUpdate}
                    loading={this.state.loading}
                    nrMeasurements={this.state.nrMeasurements}
                    openReport={(reportUuid) => this.openReport(reportUuid)}
                    reload={(json) => this.reload(json)}
                    reportDate={this.state.reportDate}
                    reportUuid={this.state.reportUuid}
                    reports={this.state.reports}
                    reportsOverview={this.state.reportsOverview}
                    setUser={(username, email, sessionExpirationDateTime) =>
                        this.setUserSession(username, email, sessionExpirationDateTime)
                    }
                    user={this.state.user}
                />
            </ThemeProvider>
        )
    }
}

export default App
