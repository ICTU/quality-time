import React, { useEffect } from 'react';
import PropTypes from 'prop-types';
import { ToastContainer } from 'react-toastify';
import HashLinkObserver from "react-hash-link";
import useLocalStorageState from 'use-local-storage-state';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';

import { DataModel } from './context/DataModel';
import { DarkMode } from './context/DarkMode';
import { Permissions } from './context/Permissions';
import { Menubar } from './header_footer/Menubar';
import { Footer } from './header_footer/Footer';
import { SettingsPanel } from './header_footer/SettingsPanel';
import { PageContent } from './PageContent';
import { getReportsTags, getUserPermissions, userPrefersDarkMode } from './utils'
import { datePropType, optionalDatePropType, reportsOverviewPropType, reportsPropType, stringsPropType } from './sharedPropTypes';
import { useSettings } from './app_ui_settings';

export function AppUI({
    changed_fields,
    datamodel,
    email,
    handleDateChange,
    last_update,
    loading,
    nrMeasurements,
    openReportsOverview,
    openReport,
    reload,
    report_date,
    report_uuid,
    reports,
    reports_overview,
    set_user,
    user
}) {
    const [uiMode, setUIMode] = useLocalStorageState("ui_mode", { "defaultValue": "follow_os" })
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

    const user_permissions = getUserPermissions(user, email, report_date, reports_overview.permissions || {})
    const atReportsOverview = report_uuid === ""
    const current_report = atReportsOverview ? null : reports.filter((report) => report.report_uuid === report_uuid)[0];
    const settings = useSettings(report_uuid)

    function handleSort(column) {
        if (column === null) {
            settings.sortColumn.set("")  // Stop sorting
            return
        }
        if (settings.sortColumn.equals(column)) {
            if (settings.sortDirection.equals('descending')) {
                settings.sortColumn.set("")  // Cycle through ascending->descending->no sort as long as the user clicks the same column
            }
            settings.sortDirection.set(settings.sortDirection.equals('ascending') ? 'descending' : 'ascending')
        } else {
            settings.sortColumn.set(column)
        }
    }

    const darkMode = userPrefersDarkMode(uiMode);
    const backgroundColor = darkMode ? "rgb(40, 40, 40)" : "white"
    return (
        <div style={{ display: "flex", minHeight: "100vh", flexDirection: "column", backgroundColor: backgroundColor }}>
            <DarkMode.Provider value={darkMode}>
                <HashLinkObserver />
                <Menubar
                    atReportsOverview={atReportsOverview}
                    email={email}
                    openReportsOverview={openReportsOverview}
                    onDate={handleDateChange}
                    report_date={report_date}
                    set_user={set_user}
                    user={user}
                    visibleDetailsTabs={settings.visibleDetailsTabs}
                    panel={<SettingsPanel
                        atReportsOverview={atReportsOverview}
                        handleDateChange={handleDateChange}
                        handleSort={handleSort}
                        settings={settings}
                        reportDate={report_date}
                        tags={getReportsTags(reports)}
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
                            handleSort={handleSort}
                            loading={loading}
                            nrMeasurements={nrMeasurements}
                            openReportsOverview={openReportsOverview}
                            openReport={openReport}
                            reload={reload}
                            report_date={report_date}
                            report_uuid={report_uuid}
                            reports={reports}
                            reports_overview={reports_overview}
                            settings={settings}
                        />
                    </DataModel.Provider>
                </Permissions.Provider>
                <Footer last_update={last_update} report={current_report} />
            </DarkMode.Provider>
        </div>
    )
}
AppUI.propTypes = {
    changed_fields: stringsPropType,
    datamodel: PropTypes.object,
    email: PropTypes.string,
    handleDateChange: PropTypes.func,
    last_update: datePropType,
    loading: PropTypes.bool,
    nrMeasurements: PropTypes.number,
    openReport: PropTypes.func,
    openReportsOverview: PropTypes.func,
    reload: PropTypes.func,
    report_date: optionalDatePropType,
    report_uuid: PropTypes.string,
    reports: reportsPropType,
    reports_overview: reportsOverviewPropType,
    set_user: PropTypes.func,
    user: PropTypes.string
}
