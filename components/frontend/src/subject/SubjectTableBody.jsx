import { TableBody } from "@mui/material"
import { array, func, string } from "prop-types"

import {
    datesPropType,
    measurementsPropType,
    optionalDatePropType,
    reportPropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
} from "../sharedPropTypes"
import { SubjectTableRow } from "./SubjectTableRow"

export function SubjectTableBody({
    changedFields,
    columnsToHide,
    dates,
    handleSort,
    measurements,
    metricEntries,
    reload,
    report,
    reportDate,
    reports,
    reversedMeasurements,
    settings,
    subjectUuid,
}) {
    const lastIndex = metricEntries.length - 1
    return (
        <TableBody>
            {metricEntries.map(([metricUuid, metric], index) => {
                return (
                    <SubjectTableRow
                        changedFields={changedFields}
                        dates={dates}
                        columnsToHide={columnsToHide}
                        handleSort={handleSort}
                        index={index}
                        key={metricUuid}
                        lastIndex={lastIndex}
                        measurements={measurements}
                        metricUuid={metricUuid}
                        metric={metric}
                        reload={reload}
                        report={report}
                        reportDate={reportDate}
                        reports={reports}
                        reversedMeasurements={reversedMeasurements}
                        settings={settings}
                        subjectUuid={subjectUuid}
                    />
                )
            })}
        </TableBody>
    )
}
SubjectTableBody.propTypes = {
    changedFields: stringsPropType,
    columnsToHide: stringsPropType,
    dates: datesPropType,
    handleSort: func,
    measurements: measurementsPropType,
    metricEntries: array,
    reload: func,
    report: reportPropType,
    reportDate: optionalDatePropType,
    reports: reportsPropType,
    reversedMeasurements: measurementsPropType,
    settings: settingsPropType,
    subjectUuid: string,
}
