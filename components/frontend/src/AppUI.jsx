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
import { getReportsTags, getUserPermissions } from "./utils"

export function AppUI({
    changed_fields,
    dataModel,
    email,
    handleDateChange,
    lastUpdate,
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
    user,
}) {
    const { mode, setMode } = useColorScheme()
    const user_permissions = getUserPermissions(user, email, report_date, reports_overview.permissions || {})
    const atReportsOverview = report_uuid === ""
    const current_report = atReportsOverview ? null : reports.filter((report) => report.report_uuid === report_uuid)[0]
    const settings = useSettings(report_uuid)

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
                report_date={report_date}
                report_uuid={report_uuid}
                set_user={set_user}
                user={user}
                panel={
                    <SettingsPanel
                        atReportsOverview={atReportsOverview}
                        handleSort={handleSort}
                        settings={settings}
                        tags={getReportsTags(reports)}
                    />
                }
                settings={settings}
                setUIMode={setMode}
                uiMode={mode}
            />
            <Permissions.Provider value={user_permissions}>
                <DataModel.Provider value={dataModel}>
                    <PageContent
                        changed_fields={changed_fields}
                        current_report={current_report}
                        handleSort={handleSort}
                        lastUpdate={lastUpdate}
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
            <Footer lastUpdate={lastUpdate} report={current_report} />
        </LocalizationProvider>
    )
}
AppUI.propTypes = {
    changed_fields: stringsPropType,
    dataModel: object,
    email: string,
    handleDateChange: func,
    lastUpdate: datePropType,
    loading: bool,
    nrMeasurements: number,
    openReport: func,
    openReportsOverview: func,
    reload: func,
    report_date: optionalDatePropType,
    report_uuid: string,
    reports: reportsPropType,
    reports_overview: reportsOverviewPropType,
    set_user: func,
    user: string,
}
