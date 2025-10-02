import "react-toastify/dist/ReactToastify.css"
import "./App.css"

import { useColorScheme } from "@mui/material/styles"
import { LocalizationProvider } from "@mui/x-date-pickers"
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs"
import { bool, func, number, object, string } from "prop-types"

import { useSettings } from "./app_ui_settings"
import { DataModel } from "./context/DataModel"
import { Permissions } from "./context/Permissions"
import { Footer } from "./header_footer/Footer"
import { Menubar } from "./header_footer/Menubar"
import { SettingsPanel } from "./header_footer/SettingsPanel"
import { adapterLocale } from "./locale"
import { PageContent } from "./PageContent"
import {
    datePropType,
    optionalDatePropType,
    reportsOverviewPropType,
    reportsPropType,
    stringsPropType,
} from "./sharedPropTypes"
import { getReportsTags, getReportTags, getUserPermissions } from "./utils"

export function AppUI({
    changedFields,
    dataModel,
    email,
    handleDateChange,
    lastUpdate,
    loading,
    nrMeasurements,
    openReportsOverview,
    openReport,
    reload,
    reportDate,
    reportUuid,
    reports,
    reportsOverview,
    setUser,
    user,
}) {
    const { mode, setMode } = useColorScheme()
    const userPermissions = getUserPermissions(user, email, reportDate, reportsOverview.permissions || {})
    const atReportsOverview = reportUuid === ""
    const currentReport = atReportsOverview ? null : reports.filter((report) => report.report_uuid === reportUuid)[0]
    const settings = useSettings(reportUuid)

    function handleSort(column) {
        if (column === null) {
            settings.sortColumn.set("") // Stop sorting
            return
        }
        if (settings.sortColumn.equals(column)) {
            if (settings.sortDirection.equals("descending")) {
                settings.sortColumn.set("") // Cycle through ascending->descending->no sort as long as the user clicks the same column
            }
            settings.sortDirection.set(settings.sortDirection.equals("ascending") ? "descending" : "ascending")
        } else {
            settings.sortColumn.set(column)
        }
    }

    return (
        <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale={adapterLocale(settings.language.value)}>
            <Menubar
                email={email}
                handleDateChange={handleDateChange}
                openReportsOverview={openReportsOverview}
                onDate={handleDateChange}
                reportDate={reportDate}
                reportUuid={reportUuid}
                setUser={setUser}
                user={user}
                panel={
                    <SettingsPanel
                        atReportsOverview={atReportsOverview}
                        handleSort={handleSort}
                        settings={settings}
                        tags={atReportsOverview ? getReportsTags(reports) : getReportTags(currentReport)}
                    />
                }
                settings={settings}
                setUIMode={setMode}
                uiMode={mode}
            />
            <Permissions.Provider value={userPermissions}>
                <DataModel.Provider value={dataModel}>
                    <PageContent
                        changedFields={changedFields}
                        currentReport={currentReport}
                        handleSort={handleSort}
                        lastUpdate={lastUpdate}
                        loading={loading}
                        nrMeasurements={nrMeasurements}
                        openReportsOverview={openReportsOverview}
                        openReport={openReport}
                        reload={reload}
                        reportDate={reportDate}
                        reportUuid={reportUuid}
                        reports={reports}
                        reportsOverview={reportsOverview}
                        settings={settings}
                    />
                </DataModel.Provider>
            </Permissions.Provider>
            <Footer lastUpdate={lastUpdate} report={currentReport} />
        </LocalizationProvider>
    )
}
AppUI.propTypes = {
    changedFields: stringsPropType,
    dataModel: object,
    email: string,
    handleDateChange: func,
    lastUpdate: datePropType,
    loading: bool,
    nrMeasurements: number,
    openReport: func,
    openReportsOverview: func,
    reload: func,
    reportDate: optionalDatePropType,
    reportUuid: string,
    reports: reportsPropType,
    reportsOverview: reportsOverviewPropType,
    setUser: func,
    user: string,
}
