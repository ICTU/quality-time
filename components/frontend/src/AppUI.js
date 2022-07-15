import React, { useEffect } from 'react';
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
    const [dateInterval, setDateInterval] = useURLSearchQuery(history, "date_interval", "integer", 7);
    const [dateOrder, setDateOrder] = useURLSearchQuery(history, "date_order", "string", "descending");
    const [hiddenColumns, toggleHiddenColumn, clearHiddenColumns] = useURLSearchQuery(history, "hidden_columns", "array");
    const [hideMetricsNotRequiringAction, setHideMetricsNotRequiringAction] = useURLSearchQuery(history, "hide_metrics_not_requiring_action", "boolean", false);
    const [nrDates, setNrDates] = useURLSearchQuery(history, "nr_dates", "integer", 1);
    const [sortColumn, setSortColumn] = useURLSearchQuery(history, "sort_column", "string", null);
    const [sortDirection, setSortDirection] = useURLSearchQuery(history, "sort_direction", "string", "ascending");
    const [visibleDetailsTabs, toggleVisibleDetailsTab, clearVisibleDetailsTabs] = useURLSearchQuery(history, "tabs", "array");
    const [showIssueSummary, setShowIssueSummary] = useURLSearchQuery(history, "show_issue_summary", "boolean", false);
    const [showIssueCreationDate, setShowIssueCreationDate] = useURLSearchQuery(history, "show_issue_creation_date", "boolean", false);
    const [showIssueUpdateDate, setShowIssueUpdateDate] = useURLSearchQuery(history, "show_issue_update_date", "boolean", false);
    const [showIssueDueDate, setShowIssueDueDate] = useURLSearchQuery(history, "show_issue_due_date", "boolean", false);

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
                    current_report={current_report}
                    email={email}
                    go_home={go_home}
                    onDate={handleDateChange}
                    report_date_string={report_date_string}
                    set_user={set_user}
                    user={user}
                    panel={<ViewPanel
                        clearHiddenColumns={clearHiddenColumns}
                        clearVisibleDetailsTabs={clearVisibleDetailsTabs}
                        dateInterval={dateInterval}
                        dateOrder={dateOrder}
                        handleSort={handleSort}
                        hiddenColumns={hiddenColumns}
                        hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
                        nrDates={nrDates}
                        setDateInterval={setDateInterval}
                        setDateOrder={setDateOrder}
                        setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction}
                        setNrDates={setNrDates}
                        setShowIssueCreationDate={setShowIssueCreationDate}
                        setShowIssueSummary={setShowIssueSummary}
                        setShowIssueUpdateDate={setShowIssueUpdateDate}
                        setShowIssueDueDate={setShowIssueDueDate}
                        setUIMode={setUIMode}
                        showIssueCreationDate={showIssueCreationDate}
                        showIssueSummary={showIssueSummary}
                        showIssueUpdateDate={showIssueUpdateDate}
                        showIssueDueDate={showIssueDueDate}
                        sortColumn={sortColumn}
                        sortDirection={sortDirection}
                        toggleHiddenColumn={toggleHiddenColumn}
                        uiMode={uiMode}
                        visibleDetailsTabs={visibleDetailsTabs}
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
                            showIssueCreationDate={showIssueCreationDate}
                            showIssueSummary={showIssueSummary}
                            showIssueUpdateDate={showIssueUpdateDate}
                            showIssueDueDate={showIssueDueDate}
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
