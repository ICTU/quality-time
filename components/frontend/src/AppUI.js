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
<<<<<<< HEAD
    show_issue_due_date: false,
    show_issue_release: false,
    show_issue_sprint: false
=======
    uiMode: null
>>>>>>> 9b31ee2b (one settings object)
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
    const [defaultSettings, setDefaultSettings] = useState(DEFAULT_SETTINGS)
    const [uiMode, setUIMode] = useURLSearchQuery(history, "ui_mode", "string", null);
    useEffect(() => {
        const mediaQueryList = window.matchMedia("(prefers-color-scheme: dark)");
        mediaQueryList.addEventListener("change", changeMode);
        function changeMode(e) {
            if (uiMode === null) {  // Only update if the user is following the OS mode setting
                setUIMode(e.matches ? "dark" : "light")  // Force redraw
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

    useEffect(() => {
        const userSettings = get_settings()
        setDefaultSettings({...defaultSettings, ...userSettings})
    }, [])

    const [dateInterval, setDateInterval] = useURLSearchQuery(history, "date_interval", "integer", defaultSettings.date_interval);
    const [dateOrder, setDateOrder] = useURLSearchQuery(history, "date_order", "string", defaultSettings.date_order);
    const [hiddenColumns, toggleHiddenColumn, setHiddenColumns] = useURLSearchQuery(history, "hidden_columns", "array", defaultSettings.hidden_columns);
    const [hideMetricsNotRequiringAction, setHideMetricsNotRequiringAction] = useURLSearchQuery(history, "hide_metrics_not_requiring_action", "boolean", defaultSettings.hide_metrics_not_requiring_action);
    const [nrDates, setNrDates] = useURLSearchQuery(history, "nr_dates", "integer", defaultSettings.nr_dates);
    const [sortColumn, setSortColumn] = useURLSearchQuery(history, "sort_column", "string", defaultSettings.sort_column);
    const [sortDirection, setSortDirection] = useURLSearchQuery(history, "sort_direction", "string", defaultSettings.sort_direction);
    const [visibleDetailsTabs, toggleVisibleDetailsTab, setVisibleDetailsTabs] = useURLSearchQuery(history, "tabs", "array", defaultSettings.tabs);
    const [showIssueSummary, setShowIssueSummary] = useURLSearchQuery(history, "show_issue_summary", "boolean", defaultSettings.show_issue_summary);
    const [showIssueCreationDate, setShowIssueCreationDate] = useURLSearchQuery(history, "show_issue_creation_date", "boolean", defaultSettings.show_issue_creation_date);
    const [showIssueUpdateDate, setShowIssueUpdateDate] = useURLSearchQuery(history, "show_issue_update_date", "boolean", defaultSettings.show_issue_update_date);
    const [showIssueDueDate, setShowIssueDueDate] = useURLSearchQuery(history, "show_issue_due_date", "boolean", defaultSettings.show_issue_due_date);
    const [showIssueRelease, setShowIssueRelease] = useURLSearchQuery(history, "show_issue_release", "boolean", defaultSettings.show_issue_release);
    const [showIssueSprint, setShowIssueSprint] = useURLSearchQuery(history, "show_issue_sprint", "boolean", defaultSettings.show_issue_sprint);

    const currentSettings = {
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
    }

    function setSettings(partialSettings) {
        const settings = {...currentSettings, ...partialSettings}
        setDateInterval(settings.date_interval)
        setDateOrder(settings.date_order)
        setHiddenColumns(settings.hidden_columns)
        setHideMetricsNotRequiringAction(settings.hide_metrics_not_requiring_action)
        setNrDates(settings.nr_dates)
        setSortColumn(settings.sort_column)
        setSortDirection(settings.sort_direction)
        setVisibleDetailsTabs(settings.tabs)
        setShowIssueSummary(settings.show_issue_summary)
        setShowIssueCreationDate(settings.show_issue_creation_date)
        setShowIssueUpdateDate(settings.showIssueUpdateDate)
        setShowIssueDueDate(settings.showIssueDueDate)
        setShowIssueRelease(settings.showIssueRelease)
        setShowIssueSprint(settings.showIssueSprint)
        setUIMode(settings.ui_mode)
    }

    function handleSort(column) {
        if (column === null) {
            setSortColumn(null)  // Stop sorting
            return
        }
        if (sortColumn === column) {
            if (sortDirection === 'descending') {
                setSortColumn(null)  // Cycle through ascending->descending->no sort as long as the user clicks the same column
            }
            setSortDirection(sortDirection === 'ascending' ? 'descending' : 'ascending')
        } else {
            setSortColumn(column)
        }
    }

    const darkMode = userPrefersDarkMode(uiMode);
    const backgroundColor = darkMode ? "rgb(40, 40, 40)" : "white"
    return (
        <div style={{ display: "flex", minHeight: "100vh", flexDirection: "column", backgroundColor: backgroundColor }}>
            <DarkMode.Provider value={darkMode}>
                <HashLinkObserver />
                <Menubar
                    clearVisibleDetailsTabs={clearVisibleDetailsTabs}
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
                        postSettings={post_settings}
                        defaultSettings={defaultSettings}
                        handleSort={handleSort}
                    />}
                />
                <ToastContainer theme="colored" />
                <Permissions.Provider value={user_permissions}>
                    <DataModel.Provider value={datamodel}>
                        <PageContent
                            changed_fields={changed_fields}
                            current_report={current_report}
                            dateInterval={dateInterval}
                            dateOrder={dateOrder}
                            go_home={go_home}
                            handleSort={handleSort}
                            hiddenColumns={hiddenColumns}
                            hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
                            history={history}
                            loading={loading}
                            nrDates={nrDates}
                            nr_measurements={nr_measurements}
                            open_report={open_report}
                            reload={reload}
                            report_date={report_date}
                            report_uuid={report_uuid}
                            reports={reports}
                            reports_overview={reports_overview}
                            sortColumn={sortColumn}
                            sortDirection={sortDirection}
                            toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                            visibleDetailsTabs={visibleDetailsTabs}
                        />
                    </DataModel.Provider>
                </Permissions.Provider>
                <Footer last_update={last_update} report={current_report} />
            </DarkMode.Provider>
        </div>
    )
}
