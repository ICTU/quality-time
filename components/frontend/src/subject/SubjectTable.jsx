import "./SubjectTable.css"

import { Table, TableContainer } from "@mui/material"
import { array, func, object, string } from "prop-types"
import { useContext } from "react"

import { DataModelContext } from "../context/DataModel"
import { reverseSortMeasurements } from "../report/report_utils"
import {
    availabilityMessagePropType,
    datesPropType,
    measurementsPropType,
    optionalDatePropType,
    reportPropType,
    reportsPropType,
    settingsPropType,
} from "../sharedPropTypes"
import { determineColumnsToHide } from "./subject_column"
import { SubjectTableBody } from "./SubjectTableBody"
import { SubjectTableFooter } from "./SubjectTableFooter"
import { SubjectTableHeader } from "./SubjectTableHeader"

export function SubjectTable({
    dates,
    fieldWithUrlAvailabilityError,
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
    const dataModel = useContext(DataModelContext)
    const columnsToHide = determineColumnsToHide(dataModel, measurements, metricEntries, dates.length, report, settings)
    return (
        <TableContainer sx={{ overflowX: "visible" }}>
            <Table className="subjectTable" stickyHeader>
                <SubjectTableHeader
                    columnDates={dates}
                    columnsToHide={columnsToHide}
                    handleSort={handleSort}
                    settings={settings}
                />
                <SubjectTableBody
                    columnsToHide={columnsToHide}
                    dates={dates}
                    fieldWithUrlAvailabilityError={fieldWithUrlAvailabilityError}
                    handleSort={handleSort}
                    measurements={measurements}
                    metricEntries={metricEntries}
                    reload={reload}
                    report={report}
                    reportDate={reportDate}
                    reports={reports}
                    reversedMeasurements={reverseSortMeasurements(measurements)}
                    settings={settings}
                    subjectUuid={subjectUuid}
                />
                <SubjectTableFooter
                    reload={reload}
                    report={report}
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
    dates: datesPropType,
    fieldWithUrlAvailabilityError: availabilityMessagePropType,
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
