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
    changed_fields,
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
    subject_uuid,
}) {
    const lastIndex = metricEntries.length - 1
    return (
        <TableBody>
            {metricEntries.map(([metric_uuid, metric], index) => {
                return (
                    <SubjectTableRow
                        changed_fields={changed_fields}
                        dates={dates}
                        handleSort={handleSort}
                        index={index}
                        key={metric_uuid}
                        lastIndex={lastIndex}
                        measurements={measurements}
                        metric_uuid={metric_uuid}
                        metric={metric}
                        reload={reload}
                        report={report}
                        reportDate={reportDate}
                        reports={reports}
                        reversedMeasurements={reversedMeasurements}
                        settings={settings}
                        subject_uuid={subject_uuid}
                    />
                )
            })}
        </TableBody>
    )
}
SubjectTableBody.propTypes = {
    changed_fields: stringsPropType,
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
    subject_uuid: string,
}
