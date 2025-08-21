import "./SubjectTable.css"

import { Table, TableContainer } from "@mui/material"
import { array, func, object, string } from "prop-types"
import { useContext } from "react"

import { DataModel } from "../context/DataModel"
import {
    datesPropType,
    measurementsPropType,
    optionalDatePropType,
    reportPropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
} from "../sharedPropTypes"
import { determineColumnsToHide } from "./subject_column"
import { SubjectTableBody } from "./SubjectTableBody"
import { SubjectTableFooter } from "./SubjectTableFooter"
import { SubjectTableHeader } from "./SubjectTableHeader"

export function SubjectTable({
    changedFields,
    dates,
    handleSort,
    measurements,
    metricEntries,
    reload,
    report,
    reportDate,
    reports,
    settings,
    subject,
    subjectUuid,
}) {
    const dataModel = useContext(DataModel)
    // Sort measurements in reverse order so that if there multiple measurements on a day, we find the most recent one:
    const reversedMeasurements = measurements.slice().sort((m1, m2) => (m1.start < m2.start ? 1 : -1))
    const columnsToHide = determineColumnsToHide(dataModel, measurements, metricEntries, dates.length, report, settings)
    return (
        <TableContainer sx={{ overflowX: "visible" }}>
            <Table
                className="subjectTable"
                stickyHeader
                sx={{
                    "& .MuiTableCell-sizeMedium": {
                        padding: "8px",
                    },
                }}
            >
                <SubjectTableHeader
                    columnDates={dates}
                    columnsToHide={columnsToHide}
                    handleSort={handleSort}
                    settings={settings}
                />
                <SubjectTableBody
                    changedFields={changedFields}
                    dates={dates}
                    columnsToHide={columnsToHide}
                    handleSort={handleSort}
                    measurements={measurements}
                    metricEntries={metricEntries}
                    reload={reload}
                    report={report}
                    reportDate={reportDate}
                    reports={reports}
                    reversedMeasurements={reversedMeasurements}
                    settings={settings}
                    subjectUuid={subjectUuid}
                />
                <SubjectTableFooter
                    reload={reload}
                    reports={reports}
                    stopFilteringAndSorting={() => {
                        handleSort(null)
                        settings.hiddenTags.reset()
                        settings.metricsToHide.reset()
                    }}
                    subject={subject}
                    subjectUuid={subjectUuid}
                />
            </Table>
        </TableContainer>
    )
}
SubjectTable.propTypes = {
    changedFields: stringsPropType,
    dates: datesPropType,
    handleSort: func,
    measurements: measurementsPropType,
    metricEntries: array,
    reload: func,
    report: reportPropType,
    reportDate: optionalDatePropType,
    reports: reportsPropType,
    settings: settingsPropType,
    subject: object,
    subjectUuid: string,
}
