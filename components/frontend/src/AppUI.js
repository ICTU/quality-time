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
import { getReportsTags, getUserPermissions, reportIsTagReport, userPrefersDarkMode, useURLSearchQuery } from './utils'

export function AppUI({
    changed_fields,
    datamodel,
    email,
    go_home,
    handleDateChange,
    last_update,
    loading,
    nrMeasurements,
    open_report,
    reload,
    report_date,
    report_uuid,
    reports,
    reports_overview,
    set_user,
    user
}) {
    const [uiMode, setUIMode] = useURLSearchQuery("ui_mode", "string", null);
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
        user, email, reportIsTagReport(report_uuid), report_date, reports_overview.permissions || {}
    )
    const current_report = reports.filter((report) => report.report_uuid === report_uuid)[0] || null;
    const [dateInterval, setDateInterval] = useURLSearchQuery("date_interval", "integer", 7);
    const [dateOrder, setDateOrder] = useURLSearchQuery("date_order", "string", "descending");
    const [hiddenColumns, toggleHiddenColumn, clearHiddenColumns] = useURLSearchQuery("hidden_columns", "array");
    const [hiddenTags, toggleHiddenTag, clearHiddenTags] = useURLSearchQuery("hidden_tags", "array");
    const [hideMetricsNotRequiringAction, setHideMetricsNotRequiringAction] = useURLSearchQuery("hide_metrics_not_requiring_action", "boolean", false);
    const [nrDates, setNrDates] = useURLSearchQuery("nr_dates", "integer", 1);
    const [sortColumn, setSortColumn] = useURLSearchQuery("sort_column", "string", null);
    const [sortDirection, setSortDirection] = useURLSearchQuery("sort_direction", "string", "ascending");
    const [visibleDetailsTabs, toggleVisibleDetailsTab, clearVisibleDetailsTabs] = useURLSearchQuery("tabs", "array");
    const [showIssueSummary, setShowIssueSummary] = useURLSearchQuery("show_issue_summary", "boolean", false);
    const [showIssueCreationDate, setShowIssueCreationDate] = useURLSearchQuery("show_issue_creation_date", "boolean", false);
    const [showIssueUpdateDate, setShowIssueUpdateDate] = useURLSearchQuery("show_issue_update_date", "boolean", false);
    const [showIssueDueDate, setShowIssueDueDate] = useURLSearchQuery("show_issue_due_date", "boolean", false);
    const [showIssueRelease, setShowIssueRelease] = useURLSearchQuery("show_issue_release", "boolean", false);
    const [showIssueSprint, setShowIssueSprint] = useURLSearchQuery("show_issue_sprint", "boolean", false);
    const issueSettings = {
        showIssueSummary: showIssueSummary,
        showIssueCreationDate: showIssueCreationDate,
        showIssueUpdateDate: showIssueUpdateDate,
        showIssueDueDate: showIssueDueDate,
        showIssueRelease: showIssueRelease,
        showIssueSprint: showIssueSprint
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
                    atHome={report_uuid === ""}
                    clearVisibleDetailsTabs={clearVisibleDetailsTabs}
                    email={email}
                    go_home={go_home}
                    onDate={handleDateChange}
                    report_date={report_date}
                    set_user={set_user}
                    user={user}
                    visibleDetailsTabs={visibleDetailsTabs}
                    panel={<ViewPanel
                        clearHiddenColumns={clearHiddenColumns}
                        clearHiddenTags={clearHiddenTags}
                        clearVisibleDetailsTabs={clearVisibleDetailsTabs}
                        dateInterval={dateInterval}
                        dateOrder={dateOrder}
                        handleDateChange={handleDateChange}
                        handleSort={handleSort}
                        hiddenColumns={hiddenColumns}
                        hiddenTags={hiddenTags}
                        hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
                        issueSettings={issueSettings}
                        nrDates={nrDates}
                        reportDate={report_date}
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
                        tags={getReportsTags(reports)}
                        toggleHiddenColumn={toggleHiddenColumn}
                        toggleHiddenTag={toggleHiddenTag}
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
                            hiddenTags={hiddenTags}
                            hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
                            issueSettings={issueSettings}
                            loading={loading}
                            nrDates={nrDates}
                            nrMeasurements={nrMeasurements}
                            open_report={open_report}
                            reload={reload}
                            report_date={report_date}
                            report_uuid={report_uuid}
                            reports={reports}
                            reports_overview={reports_overview}
                            sortColumn={sortColumn}
                            sortDirection={sortDirection}
                            toggleHiddenTag={toggleHiddenTag}
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
