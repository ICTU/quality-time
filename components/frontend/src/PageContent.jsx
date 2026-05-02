import { Box, Container } from "@mui/material"
import CircularProgress from "@mui/material/CircularProgress"
import { bool, func, number, string } from "prop-types"
import { useContext, useEffect, useMemo, useRef, useState } from "react"

import { getMeasurements } from "./api/measurement"
import { SnackbarContext } from "./context/Snackbar"
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
    currentReport,
    fieldsWithUrlAvailabilityErrors,
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
    const showMessageRef = useRef(useContext(SnackbarContext))
    const [measurements, setMeasurements] = useState([])
    const dates = useMemo(
        () => getColumnDates(reportDate, settings.dateInterval.value, settings.dateOrder.value, settings.nrDates.value),
        [reportDate, settings.dateInterval.value, settings.dateOrder.value, settings.nrDates.value],
    )
    useEffect(() => {
        const minDate = new Date([...dates].sort((d1, d2) => d1.getTime() - d2.getTime())[0])
        minDate.setHours(minDate.getHours() - 1)
        const maxDate = reportDate ? new Date(reportDate) : new Date()
        getMeasurements(minDate, maxDate)
            .then((json) => setMeasurements(json.measurements ?? []))
            .catch((error) =>
                showMessageRef.current({
                    severity: "error",
                    title: "Could not fetch measurements",
                    description: `${error.message}`,
                }),
            )
    }, [dates, reportDate, nrMeasurements])
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
            fieldsWithUrlAvailabilityErrors: fieldsWithUrlAvailabilityErrors,
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
            {content}
        </Container>
    )
}
PageContent.propTypes = {
    currentReport: reportPropType,
    fieldsWithUrlAvailabilityErrors: stringsPropType,
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
