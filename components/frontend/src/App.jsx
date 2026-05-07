import "./App.css"

import { CssBaseline } from "@mui/material"
import { ThemeProvider } from "@mui/material/styles"
import { Action } from "history"
import history from "history/browser"
import { useCallback, useEffect, useRef, useState } from "react"

import { login } from "./api/auth"
import { getDataModel } from "./api/datamodel"
import { createNrMeasurementsEventSource } from "./api/measurement"
import { getReport, getReportsOverview } from "./api/report"
import { AppUI } from "./AppUI"
import { registeredURLSearchParams, toSearchString } from "./hooks/url_search_query"
import { showURLAvailabilityMessage } from "./messages"
import { clearStoredSession, loadStoredSession, storeSession } from "./session_storage"
import { theme } from "./theme"
import { endOfDayFromISODateString, reportUuidFromPath, toISODateStringInCurrentTZ } from "./utils"
import { SnackbarAlerts } from "./widgets/SnackbarAlerts"

function historyPush(target) {
    history.push(target + toSearchString(registeredURLSearchParams()))
}

export default function App() {
    const [dataModel, setDataModel] = useState({})
    const [lastUpdate, setLastUpdate] = useState(() => new Date())
    const [reports, setReports] = useState([])
    const [reportDate, setReportDate] = useState(() =>
        endOfDayFromISODateString(registeredURLSearchParams().get("report_date") || ""),
    )
    const [reportUuid, setReportUuid] = useState(() => reportUuidFromPath(history.location.pathname))
    const [reportsOverview, setReportsOverview] = useState({})
    const [nrMeasurements, setNrMeasurements] = useState(0)
    const [loading, setLoading] = useState(true)
    const [user, setUser] = useState(null)
    const [email, setEmail] = useState(null)
    const [snackBarMessages, setSnackBarMessages] = useState([])

    // Refs synced from state, for stable reads inside long-lived callbacks (mount-effect handlers, async fetches)
    const reportUuidRef = useRef(reportUuid)
    const reportDateRef = useRef(reportDate)
    const nrMeasurementsRef = useRef(nrMeasurements)
    useEffect(() => {
        reportUuidRef.current = reportUuid
        reportDateRef.current = reportDate
        nrMeasurementsRef.current = nrMeasurements
    })

    // Refs not backed by state (opaque handles + non-rendered flags)
    const sourceRef = useRef(null)
    const sessionExpirationTimeoutRef = useRef(null)
    const fieldWithUrlAvailabilityErrorRef = useRef(null)
    const nrMeasurementsStreamConnectedRef = useRef(true) // Assume initial connection will be successful

    function showMessage(message) {
        setSnackBarMessages((messages) =>
            messages.map((m) => JSON.stringify(m)).includes(JSON.stringify(message))
                ? messages
                : [...messages, message],
        )
    }

    function hideMessage(message) {
        setSnackBarMessages((messages) => messages.filter((m) => JSON.stringify(m) !== JSON.stringify(message)))
    }

    function setUserSession(username, emailArg, sessionExpirationDateTime) {
        if (username) {
            const emailAddress = emailArg?.includes("@") ? emailArg : null
            setUser(username)
            setEmail(emailAddress)
            storeSession(username, emailAddress, sessionExpirationDateTime)
            sessionExpirationTimeoutRef.current = setTimeout(
                () => onUserSessionExpiration(),
                sessionExpirationDateTime - Date.now(),
            )
        } else {
            setUser(null)
            setEmail(null)
            clearStoredSession()
            clearTimeout(sessionExpirationTimeoutRef.current)
        }
    }

    function onUserSessionExpiration() {
        setUserSession()
        showMessage({
            severity: "warning",
            title: "Your session expired",
            description: "Please log in to renew your session",
        })
    }

    function loginForwardAuth() {
        const showErrorMessage = (error) =>
            showMessage({
                severity: "error",
                title: "Login with forward authentication failed",
                description: `${error}`,
            })
        login("", "")
            .then((json) => {
                if (json.ok) {
                    setUserSession(json.email, json.email, new Date(json.session_expiration_datetime))
                    return true
                }
                return false
            })
            .catch(showErrorMessage)
        return false
    }

    function initUserSession() {
        const stored = loadStoredSession()
        if (!stored) {
            showMessage({
                severity: "info",
                title: "Not logged in",
                description: "Editing is not possible until you are logged in",
            })
        } else if (stored.sessionExpirationDateTime < new Date()) {
            onUserSessionExpiration()
        } else {
            setUserSession(stored.user, stored.email, stored.sessionExpirationDateTime)
        }
    }

    const fetchReports = useCallback(() => {
        const startReportUuid = reportUuidRef.current
        const startReportDate = reportDateRef.current
        const showErrorMessage = (error) =>
            showMessage({
                severity: "error",
                title: "Server unreachable",
                description: error ? `${error}` : "Couldn't load data from the server",
            })
        Promise.all([
            getDataModel(startReportDate),
            getReportsOverview(startReportDate),
            getReport(startReportUuid, startReportDate),
        ])
            .then(([newDataModel, newReportsOverview, newReports]) => {
                if (reportUuidRef.current !== startReportUuid) {
                    return // User navigated to a different report or to the overview page, cancel update
                }
                if (newDataModel.ok === false || newReports.ok === false) {
                    showErrorMessage()
                } else {
                    setDataModel(newDataModel)
                    setLastUpdate(new Date())
                    setLoading(false)
                    setReports(newReports.reports || [])
                    setReportsOverview(newReportsOverview)
                }
                return null
            })
            .catch((error) => showErrorMessage(error))
    }, [])

    function checkSession(json) {
        if (json.ok === false && json.status === 401) {
            setUserSession()
            if (loginForwardAuth() === false) {
                showMessage({
                    severity: "warning",
                    title: "Your session expired",
                    description: "Please log in to renew your session",
                })
            }
        }
    }

    function processResponseJSON(json) {
        const { availability } = json
        showURLAvailabilityMessage(availability, showMessage)
        fieldWithUrlAvailabilityErrorRef.current =
            availability?.status_code !== undefined && availability.status_code !== 200 ? availability : null
        checkSession(json)
        fetchReports()
    }

    function handleDateChange(date) {
        let parsed = registeredURLSearchParams()
        if (date && toISODateStringInCurrentTZ(date) < toISODateStringInCurrentTZ(new Date())) {
            // We're time traveling, set the report_date query parameter
            parsed.set("report_date", toISODateStringInCurrentTZ(date))
            const now = new Date()
            date.setHours(now.getHours(), now.getMinutes())
            if (!reportDate) {
                // We're time traveling from the present, warn the user
                showMessage({
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
        setReportDate(date)
        setLoading(true)
    }

    function openReportsOverview() {
        if (history.location.pathname !== "/") {
            historyPush("/")
            setReportUuid("")
            setLoading(true)
        }
    }

    function openReport(uuid) {
        historyPush(encodeURI(uuid))
        setReportUuid(uuid)
        setLoading(true)
    }

    // Mount-only effect: history listener, forward auth, session restore, EventSource subscription.
    // The initial fetchReports happens via the reactive effect below (which fires on first render).
    useEffect(() => {
        const unlistenHistory = history.listen(({ location, action }) => {
            if (action !== Action.Pop) return
            setReportUuid(reportUuidFromPath(location.pathname))
            setLoading(true)
        })
        loginForwardAuth()
        initUserSession()
        sourceRef.current = createNrMeasurementsEventSource({
            onInit: (newNrMeasurements) => {
                if (nrMeasurementsStreamConnectedRef.current) {
                    setNrMeasurements(newNrMeasurements)
                } else {
                    showMessage({
                        severity: "success",
                        title: "Connected to server",
                        description: "Successfully reconnected to server",
                    })
                    setNrMeasurements(newNrMeasurements)
                    nrMeasurementsStreamConnectedRef.current = true
                    fetchReports()
                }
            },
            onDelta: (newNrMeasurements) => {
                if (newNrMeasurements !== nrMeasurementsRef.current) {
                    setNrMeasurements(newNrMeasurements)
                    fetchReports()
                }
            },
            onError: () => {
                showMessage({
                    severity: "error",
                    title: "Server unreachable",
                    description: "Trying to reconnect to server...",
                })
                nrMeasurementsStreamConnectedRef.current = false
            },
        })
        return () => {
            unlistenHistory()
            sourceRef.current.close()
        }
        // eslint-disable-next-line @eslint-react/exhaustive-deps
    }, [])

    // Reactive effect: refetch when reportUuid or reportDate changes (and once on initial render).
    useEffect(() => {
        fetchReports()
    }, [reportUuid, reportDate, fetchReports])

    return (
        <ThemeProvider theme={theme}>
            <CssBaseline enableColorScheme />
            <SnackbarAlerts messages={snackBarMessages} hideMessage={hideMessage} showMessage={showMessage}>
                <AppUI
                    dataModel={dataModel}
                    email={email}
                    fieldWithUrlAvailabilityError={fieldWithUrlAvailabilityErrorRef.current}
                    handleDateChange={handleDateChange}
                    key={reportUuid} // Make sure the AppUI is refreshed whenever the current report changes
                    lastUpdate={lastUpdate}
                    loading={loading}
                    nrMeasurements={nrMeasurements}
                    openReport={openReport}
                    openReportsOverview={openReportsOverview}
                    reload={processResponseJSON}
                    reportDate={reportDate}
                    reportUuid={reportUuid}
                    reports={reports}
                    reportsOverview={reportsOverview}
                    setUser={setUserSession}
                    user={user}
                />
            </SnackbarAlerts>
        </ThemeProvider>
    )
}
