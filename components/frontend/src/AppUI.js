import React, { useEffect, useState } from 'react';
import { ToastContainer } from 'react-toastify';
import HashLinkObserver from "react-hash-link";
import 'react-toastify/dist/ReactToastify.css';
import './App.css';

import { Menubar } from './header_footer/Menubar';
import { Footer } from './header_footer/Footer';
import { ViewPanel } from './header_footer/ViewPanel';

import { DataModel } from './context/DataModel';
import { DarkMode } from './context/DarkMode';
import { Permissions } from './context/Permissions';
import { PageContent } from './PageContent';
import { getUserPermissions, userPrefersDarkMode, useURLSearchQuery } from './utils'
import { get_settings, post_settings } from './api/settings';

const DEFAULT_SETTINGS = {
    date_interval: 7,
    date_order: "descending",
    hidden_columns: [],
    hide_metrics_not_requiring_action: false,
    nr_dates: 1,
    sort_column: null,
    sort_direction: "ascending",
    tabs: [],
    show_issue_summary: false,
    show_issue_creation_date: false,
    show_issue_update_date: false,
    show_issue_due_date: false,
    show_issue_release: false,
    show_issue_sprint: false,
    ui_mode: null
}

export function AppUI({
    changed_fields,
    datamodel,
    email,
    go_home,
    handleDateChange,
    history,
    last_update,
    loading,
    nr_measurements,
    open_report,
    reload,
    report_date,
    report_date_string,
    report_uuid,
    reports,
    reports_overview,
    set_user,
    user
}) {
    const [uiMode, setUIMode] = useURLSearchQuery(history, "ui_mode", "string", null);
    useEffect(() => {
        const mediaQueryList = window.matchMedia("(prefers-color-scheme: dark)");
        mediaQueryList.addEventListener("change", changeMode);
        function changeMode(e) {
            if (uiMode === null) {  // Only update if the user is following the OS mode setting
                setSettings({ui_mode: e.matches ? "dark" : "light"})  // Force redraw
                setTimeout(() => setUIMode(null))  // Reset setting
            }
        }
        return () => {
            mediaQueryList.removeEventListener("change", changeMode);
        }
    }, [uiMode, setUIMode]);

    const user_permissions = getUserPermissions(
        user, email, report_uuid.slice(0, 4) === "tag-", report_date, reports_overview.permissions || {}
    )
    const current_report = reports.filter((report) => report.report_uuid === report_uuid)[0] || null;

    const [dateInterval, setDateInterval] = useURLSearchQuery(history, "date_interval", "integer", DEFAULT_SETTINGS.date_interval);
    const [dateOrder, setDateOrder] = useURLSearchQuery(history, "date_order", "string", DEFAULT_SETTINGS.date_order);
    const [hiddenColumns, toggleHiddenColumn, setHiddenColumns] = useURLSearchQuery(history, "hidden_columns", "array", DEFAULT_SETTINGS.hidden_columns);
    const [hideMetricsNotRequiringAction, setHideMetricsNotRequiringAction] = useURLSearchQuery(history, "hide_metrics_not_requiring_action", "boolean", DEFAULT_SETTINGS.hide_metrics_not_requiring_action);
    const [nrDates, setNrDates] = useURLSearchQuery(history, "nr_dates", "integer", DEFAULT_SETTINGS.nr_dates);
    const [sortColumn, setSortColumn] = useURLSearchQuery(history, "sort_column", "string", DEFAULT_SETTINGS.sort_column);
    const [sortDirection, setSortDirection] = useURLSearchQuery(history, "sort_direction", "string", DEFAULT_SETTINGS.sort_direction);
    const [visibleDetailsTabs, toggleVisibleDetailsTab, setVisibleDetailsTabs] = useURLSearchQuery(history, "tabs", "array", DEFAULT_SETTINGS.tabs);
    const [showIssueSummary, setShowIssueSummary] = useURLSearchQuery(history, "show_issue_summary", "boolean", DEFAULT_SETTINGS.show_issue_summary);
    const [showIssueCreationDate, setShowIssueCreationDate] = useURLSearchQuery(history, "show_issue_creation_date", "boolean", DEFAULT_SETTINGS.show_issue_creation_date);
    const [showIssueUpdateDate, setShowIssueUpdateDate] = useURLSearchQuery(history, "show_issue_update_date", "boolean", DEFAULT_SETTINGS.show_issue_update_date);
    const [showIssueDueDate, setShowIssueDueDate] = useURLSearchQuery(history, "show_issue_due_date", "boolean", DEFAULT_SETTINGS.show_issue_due_date);
    const [showIssueRelease, setShowIssueRelease] = useURLSearchQuery(history, "show_issue_release", "boolean", DEFAULT_SETTINGS.show_issue_release);
    const [showIssueSprint, setShowIssueSprint] = useURLSearchQuery(history, "show_issue_sprint", "boolean", DEFAULT_SETTINGS.show_issue_sprint);

    const [userSettings, setUserSettings] = useState({})
    const [currentSettings, setCurrentSettings] = useState({
        date_interval: dateInterval,
        date_order: dateOrder,
        hidden_columns: hiddenColumns,
        hide_metrics_not_requiring_action: hideMetricsNotRequiringAction,
        nr_dates: nrDates,
        sort_column: sortColumn,
        sort_direction: sortDirection,
        tabs: visibleDetailsTabs,
        show_issue_summary: showIssueSummary,
        show_issue_creation_date: showIssueCreationDate,
        show_issue_update_date: showIssueUpdateDate,
        show_issue_due_date: showIssueDueDate,
        show_issue_release: showIssueRelease,
        show_issue_sprint: showIssueSprint,
        ui_mode: uiMode
    })

    useEffect(() => {
        get_settings().then((settingsResponse) => {
            let newSettings = DEFAULT_SETTINGS
            // apparently, the response object only contains the content in the case of success, but also a status code in the case of failure
            if (settingsResponse.status === undefined) {
                setUserSettings(settingsResponse.settings)
                newSettings = {...currentSettings, ...settingsResponse.settings}
            }
            setCurrentSettings(newSettings)
        })
    }, [user])

    function postSettings(settings) {
        setUserSettings(settings)
        post_settings(settings)
    }

    function setSettings(partialSettings) {
        const newSettings = {...currentSettings, ...partialSettings}
        setCurrentSettings(newSettings)
        setDateInterval(newSettings.date_interval)
        setDateOrder(newSettings.date_order)
        setHiddenColumns(newSettings.hidden_columns)
        setHideMetricsNotRequiringAction(newSettings.hide_metrics_not_requiring_action)
        setNrDates(newSettings.nr_dates)
        setSortColumn(newSettings.sort_column)
        setSortDirection(newSettings.sort_direction)
        setVisibleDetailsTabs(newSettings.tabs)
        setShowIssueSummary(newSettings.show_issue_summary)
        setShowIssueCreationDate(newSettings.show_issue_creation_date)
        setShowIssueUpdateDate(newSettings.show_issue_update_date)
        setShowIssueDueDate(newSettings.show_issue_due_date)
        setShowIssueRelease(newSettings.show_issue_release)
        setShowIssueSprint(newSettings.show_issue_sprint)
        setUIMode(newSettings.ui_mode)
    }

    function handleSort(column) {
        const sortSettings = {}
        if (column === null) {
            sortSettings.sort_column = null
        }
        else if (currentSettings.sort_column === column) {
            if (currentSettings.sort_direction === 'descending') {
                sortSettings.sort_column = null
            }
            sortSettings.sort_direction = currentSettings.sort_direction === 'ascending' ? 'descending' : 'ascending'
        } else {
            sortSettings.sort_column = column
        }
        setSettings(sortSettings)
    }

    const darkMode = userPrefersDarkMode(currentSettings.ui_mode);
    const backgroundColor = darkMode ? "rgb(40, 40, 40)" : "white"
    return (
        <div style={{ display: "flex", minHeight: "100vh", flexDirection: "column", backgroundColor: backgroundColor }}>
            <DarkMode.Provider value={darkMode}>
                <HashLinkObserver />
                <Menubar
                    setVisibleDetailsTabs={setVisibleDetailsTabs}
                    current_report={current_report}
                    email={email}
                    go_home={go_home}
                    onDate={handleDateChange}
                    report_date_string={report_date_string}
                    set_user={set_user}
                    user={user}
                    visibleDetailsTabs={visibleDetailsTabs}
                    panel={<ViewPanel
                        settings={currentSettings}
                        setSettings={setSettings}
                        toggleHiddenColumn={toggleHiddenColumn}
                        postSettings={postSettings}
                        userSettings={userSettings}
                        handleSort={handleSort}
                        user={user}
                    />}
                />
                <ToastContainer theme="colored" />
                <Permissions.Provider value={user_permissions}>
                    <DataModel.Provider value={datamodel}>
                        <PageContent
                            changed_fields={changed_fields}
                            current_report={current_report}
                            settings={currentSettings}
                            go_home={go_home}
                            handleSort={handleSort}
                            history={history}
                            loading={loading}
                            nr_measurements={nr_measurements}
                            open_report={open_report}
                            reload={reload}
                            report_date={report_date}
                            report_uuid={report_uuid}
                            reports={reports}
                            reports_overview={reports_overview}
                            toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                        />
                    </DataModel.Provider>
                </Permissions.Provider>
                <Footer last_update={last_update} report={current_report} />
            </DarkMode.Provider>
        </div>
    )
}
