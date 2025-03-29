import { bool, func } from "prop-types"

import { useDelayedRender } from "../hooks/delayed_render"
import {
    datesPropType,
    measurementsPropType,
    optionalDatePropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
} from "../sharedPropTypes"
import { Subject } from "./Subject"

export function Subjects({
    atReportsOverview,
    changedFields,
    dates,
    handleSort,
    measurements,
    reload,
    reports,
    reportsToShow,
    reportDate,
    settings,
}) {
    // Assume max 3 subjects are visible below the dashboard when the page is initially rendered
    const nrSubjectsVisibleOnInitialRender = 3
    const visible = useDelayedRender()
    const subjects = []
    reportsToShow.forEach((report) => {
        const lastIndex = Object.keys(report.subjects).length - 1
        Object.keys(report.subjects).forEach((subjectUuid, index) => {
            if (!visible && subjects.length > nrSubjectsVisibleOnInitialRender) {
                return
            }
            subjects.push(
                <Subject
                    atReportsOverview={atReportsOverview}
                    changedFields={changedFields}
                    dates={dates}
                    firstSubject={index === 0}
                    handleSort={handleSort}
                    key={subjectUuid}
                    lastSubject={index === lastIndex}
                    measurements={measurements}
                    reload={reload}
                    report={report}
                    reports={reports}
                    reportDate={reportDate}
                    settings={settings}
                    subjectUuid={subjectUuid}
                />,
            )
        })
    })
    return subjects
}
Subjects.propTypes = {
    atReportsOverview: bool,
    changedFields: stringsPropType,
    dates: datesPropType,
    handleSort: func,
    measurements: measurementsPropType,
    reload: func,
    reports: reportsPropType,
    reportsToShow: reportsPropType,
    reportDate: optionalDatePropType,
    settings: settingsPropType,
}
