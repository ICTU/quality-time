import "./App.css"

import { CssBaseline } from "@mui/material"
import { ThemeProvider } from "@mui/material/styles"
import { Action } from "history"
import history from "history/browser"
import { Component } from "react"

import { login } from "./api/auth"
import { getDataModel } from "./api/datamodel"
import { createNrMeasurementsEventSource } from "./api/measurement"
import { getReport, getReportsOverview } from "./api/report"
import { AppUI } from "./AppUI"
import { registeredURLSearchParams, toSearchString } from "./hooks/url_search_query"
import { showURLAvailabilityMessages } from "./messages"
import { clearStoredSession, loadStoredSession, storeSession } from "./session_storage"
import { theme } from "./theme"
import { endOfDayFromISODateString, reportUuidFromPath, toISODateStringInCurrentTZ } from "./utils"
import { SnackbarAlerts } from "./widgets/SnackbarAlerts"

class App extends Component {
    constructor(props) {
        super(props)
        const reportUuid = reportUuidFromPath(history.location.pathname)
        const reportDate = endOfDayFromISODateString(registeredURLSearchParams().get("report_date") || "")
        this.state = {
            dataModel: {},
            lastUpdate: new Date(),
            reports: [],
            reportDate: reportDate,
            reportUuid: reportUuid,
            reportsOverview: {},
            nrMeasurements: 0,
            nrMeasurementsStreamConnected: true, // Assume initial connection will be successful
            loading: true,
            user: null,
            email: null,
            snackBarMessages: [],
        }
        history.listen(({ location, action }) => this.onHistory({ location, action }))
    }

    onHistory({ location, action }) {
        if (action === Action.Pop) {
            const reportUuid = reportUuidFromPath(location.pathname)
            this.setState({ reportUuid: reportUuid, loading: true }, () => this.reload())
        }
    }

    componentDidMount() {
        this.loginForwardAuth()
        this.initUserSession()
        this.connectToNrMeasurementsEventSource()
        this.reload()
    }

    componentWillUnmount() {
        this.source.close()
    }

    showMessage(message) {
        if (!this.state.snackBarMessages.map((m) => JSON.stringify(m)).includes(JSON.stringify(message))) {
            this.setState((state) => ({
                snackBarMessages: [...state.snackBarMessages, message],
            }))
        }
    }

    hideMessage(message) {
        this.setState((state) => ({
            snackBarMessages: state.snackBarMessages.filter((m) => JSON.stringify(m) !== JSON.stringify(message)),
        }))
    }

    reload(json) {
        if (json) {
            showURLAvailabilityMessages(json.availability, (message) => this.showMessage(message))
            this.fieldsWithUrlAvailabilityErrors = json.availability
                ? json.availability.filter((urlKey) => urlKey.status_code !== 200)
                : null
            this.checkSession(json)
        }
        this.loadAndSetState()
    }

    loadAndSetState() {
        const reportUuid = this.state.reportUuid
        const reportDate = this.state.reportDate
        const showErrorMessage = (error) =>
            this.showMessage({
                severity: "error",
                title: "Server unreachable",
                description: error ?? "Couldn't load data from the server",
            })
        Promise.all([getDataModel(reportDate), getReportsOverview(reportDate), getReport(reportUuid, reportDate)])
            .then(([dataModel, reportsOverview, reports]) => {
                if (this.state.reportUuid !== reportUuid) {
                    return // User navigated to a different report or to the overview page, cancel update
                }
                if (dataModel.ok === false || reports.ok === false) {
                    showErrorMessage()
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
            .catch((error) => showErrorMessage(error))
    }

    checkSession(json) {
        if (json.ok === false && json.status === 401) {
            this.setUserSession()
            if (this.loginForwardAuth() === false) {
                this.showMessage({
                    severity: "warning",
                    title: "Your session expired",
                    description: "Please log in to renew your session",
                })
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
                this.showMessage({
                    severity: "info",
                    title: "Historic information is read-only",
                    description: "Editing is not possible while you are viewing historic information",
                })
            }
        } else {
            // We're (back) in the present
            parsed.delete("report_date")
            date = null
        }
        history.replace({ search: toSearchString(parsed) })
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
        history.push(target + toSearchString(registeredURLSearchParams()))
    }

    connectToNrMeasurementsEventSource() {
        this.source = createNrMeasurementsEventSource({
            onInit: (newNrMeasurements) => {
                if (this.state.nrMeasurementsStreamConnected) {
                    this.setState({ nrMeasurements: newNrMeasurements })
                } else {
                    this.showMessage({
                        severity: "success",
                        title: "Connected to server",
                        description: "Successfully reconnected to server",
                    })
                    this.setState({ nrMeasurements: newNrMeasurements, nrMeasurementsStreamConnected: true }, () =>
                        this.reload(),
                    )
                }
            },
            onDelta: (newNrMeasurements) => {
                if (newNrMeasurements !== this.state.nrMeasurements) {
                    this.setState({ nrMeasurements: newNrMeasurements }, () => this.reload())
                }
            },
            onError: () => {
                this.showMessage({
                    severity: "error",
                    title: "Server unreachable",
                    description: "Trying to reconnect to server...",
                })
                this.setState({ nrMeasurementsStreamConnected: false })
            },
        })
    }

    loginForwardAuth() {
        const showErrorMessage = (error) =>
            this.showMessage({
                severity: "error",
                title: "Login with forward authentication failed",
                description: `${error}`,
            })
        login("", "")
            .then((json) => {
                if (json.ok) {
                    this.setUserSession(json.email, json.email, new Date(json.session_expiration_datetime))
                    return true
                }
                return false
            })
            .catch(showErrorMessage)
        return false
    }

    initUserSession() {
        const stored = loadStoredSession()
        if (!stored) {
            this.showMessage({
                severity: "info",
                title: "Not logged in",
                description: "Editing is not possible until you are logged in",
            })
        } else if (stored.sessionExpirationDateTime < new Date()) {
            this.onUserSessionExpiration()
        } else {
            this.setUserSession(stored.user, stored.email, stored.sessionExpirationDateTime)
        }
    }

    setUserSession(username, email, sessionExpirationDateTime) {
        if (username) {
            const emailAddress = email?.includes("@") ? email : null
            this.setState({ user: username, email: emailAddress })
            storeSession(username, emailAddress, sessionExpirationDateTime)
            this.sessionExpirationTimeoutId = setTimeout(
                () => this.onUserSessionExpiration(),
                sessionExpirationDateTime - Date.now(),
            )
        } else {
            this.setState({ user: null, email: null })
            clearStoredSession()
            clearTimeout(this.sessionExpirationTimeoutId)
        }
    }

    onUserSessionExpiration() {
        this.setUserSession()
        this.showMessage({
            severity: "warning",
            title: "Your session expired",
            description: "Please log in to renew your session",
        })
    }

    render() {
        return (
            <ThemeProvider theme={theme}>
                <CssBaseline enableColorScheme />
                <SnackbarAlerts
                    messages={this.state.snackBarMessages}
                    hideMessage={(message) => this.hideMessage(message)}
                    showMessage={(message) => this.showMessage(message)}
                >
                    <AppUI
                        dataModel={this.state.dataModel}
                        email={this.state.email}
                        fieldsWithUrlAvailabilityErrors={this.fieldsWithUrlAvailabilityErrors}
                        handleDateChange={(date) => this.handleDateChange(date)}
                        key={this.state.reportUuid} // Make sure the AppUI is refreshed whenever the current report changes
                        lastUpdate={this.state.lastUpdate}
                        loading={this.state.loading}
                        nrMeasurements={this.state.nrMeasurements}
                        openReport={(reportUuid) => this.openReport(reportUuid)}
                        openReportsOverview={() => this.openReportsOverview()}
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
                </SnackbarAlerts>
            </ThemeProvider>
        )
    }
}

export default App
