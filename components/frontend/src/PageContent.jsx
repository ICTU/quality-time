import { Box, Container } from "@mui/material"
import CircularProgress from "@mui/material/CircularProgress"
import { bool, func, number, string } from "prop-types"
import { useEffect, useState } from "react"
import { ToastContainer } from "react-toastify"

import { getMeasurements } from "./api/measurement"
import { useHashFragment } from "./hooks/hash_fragment"
import { Report } from "./report/Report"
import { ReportsOverview } from "./report/ReportsOverview"
import {
    datePropType,
    optionalDatePropType,
    reportPropType,
    reportsOverviewPropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
} from "./sharedPropTypes"
import { showMessage } from "./widgets/toast"

function getColumnDates(reportDate, dateInterval, dateOrder, nrDates = 1) {
    const baseDate = reportDate ? new Date(reportDate) : new Date()
    const intervalLength = dateInterval ?? 1 // dateInterval is in days
    const columnDates = []
    for (let offset = 0; offset < nrDates * intervalLength; offset += intervalLength) {
        let date = new Date(baseDate)
        date.setDate(date.getDate() - offset)
        columnDates.push(date)
    }
    if (dateOrder === "ascending") {
        columnDates.reverse()
    }
    return columnDates
}

export function PageContent({
    changedFields,
    currentReport,
    handleSort,
    lastUpdate,
    loading,
    nrMeasurements,
    openReport,
    openReportsOverview,
    reload,
    reportDate,
    reportUuid,
    reports,
    reportsOverview,
    settings,
}) {
    useHashFragment(!loading)
    const dates = getColumnDates(
        reportDate,
        settings.dateInterval.value,
        settings.dateOrder.value,
        settings.nrDates.value,
    )
    const [measurements, setMeasurements] = useState([])
    useEffect(() => {
        const maxDate = reportDate ? new Date(reportDate) : new Date()
        const minDate = dates
            .slice()
            .sort((d1, d2) => {
                return d1.getTime() - d2.getTime()
            })
            .at(0)
        minDate.setHours(minDate.getHours() - 1) // Get at least one hour of measurements
        getMeasurements(minDate, maxDate)
            .then((json) => setMeasurements(json.measurements ?? []))
            .catch((error) => showMessage("error", "Could not fetch measurements", `${error.message}`))
    }, [reportDate, nrMeasurements, settings.dateInterval.value, settings.nrDates.value])
    let content
    if (loading) {
        content = (
            <Box
                sx={{
                    alignItems: "center",
                    display: "flex",
                    width: "100%",
                    height: "60vh",
                    justifyContent: "center",
                }}
            >
                <CircularProgress aria-label="Loading..." size="6rem" />
            </Box>
        )
    } else {
        const commonProps = {
            changedFields: changedFields,
            dates: dates,
            handleSort: handleSort,
            measurements: measurements,
            reload: reload,
            reports: reports,
            reportDate: reportDate,
            settings: settings,
        }
        if (reportUuid) {
            content = (
                <Report
                    lastUpdate={lastUpdate}
                    openReportsOverview={openReportsOverview}
                    report={currentReport}
                    {...commonProps}
                />
            )
        } else {
            content = (
                <ReportsOverview
                    lastUpdate={lastUpdate}
                    openReport={openReport}
                    reportsOverview={reportsOverview}
                    {...commonProps}
                />
            )
        }
    }
    return (
        <Container
            component="main"
            disableGutters
            maxWidth={false}
            sx={{
                bgcolor: "background.default",
                flex: 1,
                paddingBottom: "50px",
                paddingTop: "10px",
                paddingLeft: "20px",
                paddingRight: "20px",
                marginTop: "60px",
                marginBottom: "0px",
                marginLeft: "0px",
                marginRight: "0px",
            }}
        >
            <ToastContainer theme="colored" />
            {content}
        </Container>
    )
}
PageContent.propTypes = {
    changedFields: stringsPropType,
    currentReport: reportPropType,
    handleSort: func,
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
    settings: settingsPropType,
}
