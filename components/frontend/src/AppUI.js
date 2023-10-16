import React, { useEffect } from 'react';
import PropTypes from 'prop-types';
import { ToastContainer } from 'react-toastify';
import HashLinkObserver from "react-hash-link";
import useLocalStorageState from 'use-local-storage-state';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';

import { Menubar } from './header_footer/Menubar';
import { Footer } from './header_footer/Footer';
import { SettingsPanel } from './header_footer/SettingsPanel';

import { DataModel } from './context/DataModel';
import { DarkMode } from './context/DarkMode';
import { Permissions } from './context/Permissions';
import { PageContent } from './PageContent';
import { getReportsTags, getUserPermissions, reportIsTagReport, userPrefersDarkMode, useURLSearchQuery } from './utils'

export function AppUI({
    changed_fields,
    datamodel,
    email,
    handleDateChange,
    last_update,
    loading,
    nrMeasurements,
    openReportsOverview,
    open_report,
    reload,
    report_date,
    report_uuid,
    reports,
    reports_overview,
    set_user,
    user
}) {
    const [uiMode, setUIMode] = useLocalStorageState("ui_mode", {"defaultValue": "follow_os"})
    useEffect(() => {
        const mediaQueryList = window.matchMedia("(prefers-color-scheme: dark)");
        mediaQueryList.addEventListener("change", changeMode);
        function changeMode(e) {
            if (uiMode === "follow_os") {  // Only update if the user is following the OS mode setting
                setUIMode(e.matches ? "dark" : "light")  // Force redraw
                setTimeout(() => setUIMode("follow_os"))  // Reset setting
            }
        }
        return () => mediaQueryList.removeEventListener("change", changeMode);
    }, [uiMode, setUIMode]);

    const user_permissions = getUserPermissions(
        user, email, reportIsTagReport(report_uuid), report_date, reports_overview.permissions || {}
    )
    const current_report = reports.filter((report) => report.report_uuid === report_uuid)[0] || null;
    // Make the settings changeable per report (and separately for the reports overview) by adding the report UUID as
    // postfix to the settings key:
    const urlSearchQueryKeyPostfix = report_uuid ? `_${report_uuid}` : ""
    const [dateInterval, setDateInterval] = useURLSearchQuery("date_interval" + urlSearchQueryKeyPostfix, "integer", 7);
    const [dateOrder, setDateOrder] = useURLSearchQuery("date_order" + urlSearchQueryKeyPostfix, "string", "descending");
    const [hiddenColumns, toggleHiddenColumn, clearHiddenColumns] = useURLSearchQuery("hidden_columns" + urlSearchQueryKeyPostfix, "array");
    const [hiddenTags, toggleHiddenTag, clearHiddenTags] = useURLSearchQuery("hidden_tags" + urlSearchQueryKeyPostfix, "array");
    const [hideMetricsNotRequiringAction, setHideMetricsNotRequiringAction] = useURLSearchQuery("hide_metrics_not_requiring_action" + urlSearchQueryKeyPostfix, "boolean", false);
    const [nrDates, setNrDates] = useURLSearchQuery("nr_dates" + urlSearchQueryKeyPostfix, "integer", 1);
    const [sortColumn, setSortColumn] = useURLSearchQuery("sort_column" + urlSearchQueryKeyPostfix, "string", null);
    const [sortDirection, setSortDirection] = useURLSearchQuery("sort_direction" + urlSearchQueryKeyPostfix, "string", "ascending");
    const [visibleDetailsTabs, toggleVisibleDetailsTab, clearVisibleDetailsTabs] = useURLSearchQuery("tabs" + urlSearchQueryKeyPostfix, "array");
    const [showIssueSummary, setShowIssueSummary] = useURLSearchQuery("show_issue_summary" + urlSearchQueryKeyPostfix, "boolean", false);
    const [showIssueCreationDate, setShowIssueCreationDate] = useURLSearchQuery("show_issue_creation_date" + urlSearchQueryKeyPostfix, "boolean", false);
    const [showIssueUpdateDate, setShowIssueUpdateDate] = useURLSearchQuery("show_issue_update_date" + urlSearchQueryKeyPostfix, "boolean", false);
    const [showIssueDueDate, setShowIssueDueDate] = useURLSearchQuery("show_issue_due_date" + urlSearchQueryKeyPostfix, "boolean", false);
    const [showIssueRelease, setShowIssueRelease] = useURLSearchQuery("show_issue_release" + urlSearchQueryKeyPostfix, "boolean", false);
    const [showIssueSprint, setShowIssueSprint] = useURLSearchQuery("show_issue_sprint" + urlSearchQueryKeyPostfix, "boolean", false);
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
    const atReportsOverview = report_uuid === ""
    return (
        <div style={{ display: "flex", minHeight: "100vh", flexDirection: "column", backgroundColor: backgroundColor }}>
            <DarkMode.Provider value={darkMode}>
                <HashLinkObserver />
                <Menubar
                    atReportsOverview={atReportsOverview}
                    clearVisibleDetailsTabs={clearVisibleDetailsTabs}
                    email={email}
                    openReportsOverview={openReportsOverview}
                    onDate={handleDateChange}
                    report_date={report_date}
                    set_user={set_user}
                    user={user}
                    visibleDetailsTabs={visibleDetailsTabs}
                    panel={<SettingsPanel
                        atReportsOverview={atReportsOverview}
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
                        sortColumn={sortColumn}
                        sortDirection={sortDirection}
                        tags={getReportsTags(reports)}
                        toggleHiddenColumn={toggleHiddenColumn}
                        toggleHiddenTag={toggleHiddenTag}
                        visibleDetailsTabs={visibleDetailsTabs}
                    />}
                    setUIMode={setUIMode}
                    uiMode={uiMode}
                />
                <ToastContainer theme="colored" />
                <Permissions.Provider value={user_permissions}>
                    <DataModel.Provider value={datamodel}>
                        <PageContent
                            changed_fields={changed_fields}
                            current_report={current_report}
                            dateInterval={dateInterval}
                            dateOrder={dateOrder}
                            openReportsOverview={openReportsOverview}
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
AppUI.propTypes = {
    openReportsOverview: PropTypes.func
}