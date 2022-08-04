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
import { getDefaultSettings, getUserPermissions, userPrefersDarkMode, useURLSearchQuery, DEFAULT_SETTINGS } from './utils'

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
    const issueSettings = {
        showIssueSummary: showIssueSummary,
        showIssueCreationDate: showIssueCreationDate,
        showIssueUpdateDate: showIssueUpdateDate,
        showIssueDueDate: showIssueDueDate,
        showIssueRelease: showIssueRelease,
        showIssueSprint: showIssueSprint
    }

    useEffect(() => {
        getDefaultSettings().then((receivedSettings) => {
            setDefaultSettings(receivedSettings)
            setDateInterval(receivedSettings.date_interval)
            setDateOrder(receivedSettings.date_order)
            setHiddenColumns(receivedSettings.hidden_columns)
            setHideMetricsNotRequiringAction(receivedSettings.hide_metrics_not_requiring_action)
            setNrDates(receivedSettings.nr_dates)
            setSortColumn(receivedSettings.sort_column)
            setVisibleDetailsTabs(receivedSettings.tabs)
            setShowIssueSummary(receivedSettings.show_issue_summary)
            setShowIssueCreationDate(receivedSettings.show_issue_creation_date)
            setShowIssueUpdateDate(receivedSettings.show_issue_update_date)
            setShowIssueDueDate(receivedSettings.show_issue_due_date)
            setShowIssueRelease(receivedSettings.show_issue_release)
            setShowIssueSprint(receivedSettings.show_issue_sprint)
            setUIMode(receivedSettings.ui_mode)
        })
    }, [])

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
                    atHome={report_uuid === ""}
                    clearVisibleDetailsTabs={clearVisibleDetailsTabs}
                    setVisibleDetailsTabs={setVisibleDetailsTabs}
                    email={email}
                    go_home={go_home}
                    onDate={handleDateChange}
                    report_date={report_date}
                    set_user={set_user}
                    user={user}
                    visibleDetailsTabs={visibleDetailsTabs}
                    panel={<ViewPanel
                        clearHiddenColumns={clearHiddenColumns}
                        clearVisibleDetailsTabs={clearVisibleDetailsTabs}
                        defaultSettings={defaultSettings}
                        setVisibleDetailsTabs={setVisibleDetailsTabs}
                        visibleDetailsTabs={visibleDetailsTabs}
                        setHiddenColumns={setHiddenColumns}
                        dateInterval={dateInterval}
                        dateOrder={dateOrder}
                        handleSort={handleSort}
                        hiddenColumns={hiddenColumns}
                        hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
                        issueSettings={issueSettings}
                        nrDates={nrDates}
                        setDateInterval={setDateInterval}
                        setDateOrder={setDateOrder}
                        setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction}
                        setNrDates={setNrDates}
                        setShowIssueCreationDate={setShowIssueCreationDate}
                        setShowIssueSummary={setShowIssueSummary}
                        setShowIssueUpdateDate={setShowIssueUpdateDate}
                        setShowIssueDueDate={setShowIssueDueDate}
                        setShowIssueRelease={setShowIssueRelease}
                        setShowIssueSprint={setShowIssueSprint}
                        setUIMode={setUIMode}
                        sortColumn={sortColumn}
                        sortDirection={sortDirection}
                        toggleHiddenColumn={toggleHiddenColumn}
                        uiMode={uiMode}
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
                            issueSettings={issueSettings}
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
