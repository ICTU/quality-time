import "./SubjectTable.css"

import { Table, TableContainer } from "@mui/material"
import { array, func, object, string } from "prop-types"

import {
    datesPropType,
    measurementsPropType,
    optionalDatePropType,
    reportPropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
} from "../sharedPropTypes"
import { SubjectTableBody } from "./SubjectTableBody"
import { SubjectTableFooter } from "./SubjectTableFooter"
import { SubjectTableHeader } from "./SubjectTableHeader"

export function SubjectTable({
    changed_fields,
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
    subject_uuid,
}) {
    // Sort measurements in reverse order so that if there multiple measurements on a day, we find the most recent one:
    const reversedMeasurements = measurements.slice().sort((m1, m2) => (m1.start < m2.start ? 1 : -1))
    return (
        <TableContainer sx={{ overflowX: "visible" }}>
            <Table
                stickyHeader
                sx={{
                    "& .MuiTableCell-sizeMedium": {
                        padding: "8px 8px",
                    },
                }}
            >
                <SubjectTableHeader columnDates={dates} handleSort={handleSort} settings={settings} />
                <SubjectTableBody
                    changed_fields={changed_fields}
                    dates={dates}
                    handleSort={handleSort}
                    measurements={measurements}
                    metricEntries={metricEntries}
                    reload={reload}
                    report={report}
                    reportDate={reportDate}
                    reports={reports}
                    reversedMeasurements={reversedMeasurements}
                    settings={settings}
                    subject_uuid={subject_uuid}
                />
                <SubjectTableFooter
                    subjectUuid={subject_uuid}
                    subject={subject}
                    reload={reload}
                    reports={reports}
                    stopFilteringAndSorting={() => {
                        handleSort(null)
                        settings.hiddenTags.reset()
                        settings.metricsToHide.reset()
                    }}
                />
            </Table>
        </TableContainer>
    )
}
SubjectTable.propTypes = {
    changed_fields: stringsPropType,
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
    subject_uuid: string,
}
