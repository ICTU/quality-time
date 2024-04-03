import "./SubjectTable.css"

import { array, func, object, string } from "prop-types"

import { Table } from "../semantic_ui_react_wrappers"
import {
    datesPropType,
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
    const className = "stickyHeader" + (subject.subtitle ? " subjectHasSubTitle" : "")
    // Sort measurements in reverse order so that if there multiple measurements on a day, we find the most recent one:
    const reversedMeasurements = measurements.slice().sort((m1, m2) => (m1.start < m2.start ? 1 : -1))
    return (
        <Table sortable className={className} style={{ marginTop: "0px" }}>
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
    )
}
SubjectTable.propTypes = {
    changed_fields: stringsPropType,
    dates: datesPropType,
    handleSort: func,
    measurements: array,
    metricEntries: array,
    reload: func,
    report: reportPropType,
    reportDate: optionalDatePropType,
    reports: reportsPropType,
    settings: settingsPropType,
    subject: object,
    subject_uuid: string,
}
