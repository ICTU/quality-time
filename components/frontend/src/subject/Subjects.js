import { array, bool, func } from "prop-types"
import {
    datesPropType,
    optionalDatePropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
} from "../sharedPropTypes"
import { useDelayedRender } from "../hooks/delayed_render"
import { Subject } from "./Subject"

export function Subjects({
    atReportsOverview,
    changed_fields,
    dates,
    handleSort,
    measurements,
    reload,
    reports,
    reportsToShow,
    report_date,
    settings,
}) {
    // Assume max 3 subjects are visible below the dashboard when the page is initially rendered
    const nrSubjectsVisibleOnInitialRender = 3
    const visible = useDelayedRender()
    const subjects = []
    reportsToShow.forEach((report) => {
        const lastIndex = Object.keys(report.subjects).length - 1
        Object.keys(report.subjects).forEach((subject_uuid, index) => {
            if (!visible && subjects.length > nrSubjectsVisibleOnInitialRender) {
                return
            }
            subjects.push(
                <Subject
                    atReportsOverview={atReportsOverview}
                    changed_fields={changed_fields}
                    dates={dates}
                    firstSubject={index === 0}
                    handleSort={handleSort}
                    key={subject_uuid}
                    lastSubject={index === lastIndex}
                    measurements={measurements}
                    reload={reload}
                    report={report}
                    reports={reports}
                    report_date={report_date}
                    settings={settings}
                    subject_uuid={subject_uuid}
                />,
            )
        })
    })
    return subjects
}
Subjects.propTypes = {
    atReportsOverview: bool,
    changed_fields: stringsPropType,
    dates: datesPropType,
    handleSort: func,
    measurements: array,
    reload: func,
    reports: reportsPropType,
    reportsToShow: reportsPropType,
    report_date: optionalDatePropType,
    settings: settingsPropType,
}
