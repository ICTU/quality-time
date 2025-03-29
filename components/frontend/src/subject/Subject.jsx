import { Divider, Paper } from "@mui/material"
import { bool, func, string } from "prop-types"
import { useContext } from "react"

import { DataModel } from "../context/DataModel"
import {
    datesPropType,
    measurementsPropType,
    metricsPropType,
    optionalDatePropType,
    reportPropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
} from "../sharedPropTypes"
import {
    getMetricComment,
    getMetricIssueIds,
    getMetricName,
    getMetricResponseOverrun,
    getMetricResponseTimeLeft,
    getMetricStatus,
    getMetricTags,
    getMetricTarget,
    getMetricUnit,
    getMetricValue,
    getSourceName,
    sortWithLocaleCompare,
    visibleMetrics,
} from "../utils"
import { CommentSegment } from "../widgets/CommentSegment"
import { SubjectTable } from "./SubjectTable"
import { SubjectTitle } from "./SubjectTitle"

function sortMetrics(dataModel, metrics, sortDirection, sortColumn, report, measurements) {
    const statusOrder = {
        unknown: "0",
        target_not_met: "1",
        near_target_met: "2",
        debt_target_met: "3",
        target_met: "4",
        informative: "5",
    }
    const sorters = {
        name: (m1, m2) => {
            const m1Name = getMetricName(m1[1], dataModel)
            const m2Name = getMetricName(m2[1], dataModel)
            return m1Name.localeCompare(m2Name)
        },
        measurement: (m1, m2) => {
            const m1Measurement = getMetricValue(m1[1], dataModel)
            const m2Measurement = getMetricValue(m2[1], dataModel)
            return m1Measurement.localeCompare(m2Measurement, undefined, { numeric: true })
        },
        target: (m1, m2) => {
            const m1Target = getMetricTarget(m1[1])
            const m2Target = getMetricTarget(m2[1])
            return m1Target.localeCompare(m2Target, undefined, { numeric: true })
        },
        comment: (m1, m2) => {
            const m1Comment = getMetricComment(m1[1])
            const m2Comment = getMetricComment(m2[1])
            return m1Comment.localeCompare(m2Comment)
        },
        status: (m1, m2) => {
            const m1Status = statusOrder[getMetricStatus(m1[1])]
            const m2Status = statusOrder[getMetricStatus(m2[1])]
            return m1Status.localeCompare(m2Status)
        },
        source: (m1, m2) => {
            let m1SourceNames = Object.values(m1[1].sources).map((source) => getSourceName(source, dataModel))
            sortWithLocaleCompare(m1SourceNames)
            let m2SourceNames = Object.values(m2[1].sources).map((source) => getSourceName(source, dataModel))
            sortWithLocaleCompare(m2SourceNames)
            return m1SourceNames.join().localeCompare(m2SourceNames.join())
        },
        issues: (m1, m2) => {
            const m1Issues = getMetricIssueIds(m1[1]).join()
            const m2Issues = getMetricIssueIds(m2[1]).join()
            return m1Issues.localeCompare(m2Issues)
        },
        tags: (m1, m2) => {
            const m1Tags = getMetricTags(m1[1]).join()
            const m2Tags = getMetricTags(m2[1]).join()
            return m1Tags.localeCompare(m2Tags)
        },
        unit: (m1, m2) => {
            const m1Unit = getMetricUnit(m1[1], dataModel)
            const m2Unit = getMetricUnit(m2[1], dataModel)
            return m1Unit.localeCompare(m2Unit)
        },
        time_left: (m1, m2) => {
            const m1TimeLeft = getMetricResponseTimeLeft(m1[1], report) ?? 0
            const m2TimeLeft = getMetricResponseTimeLeft(m2[1], report) ?? 0
            return m1TimeLeft - m2TimeLeft
        },
        overrun: (m1, m2) => {
            const m1Overrun = getMetricResponseOverrun(m1[0], m1[1], report, measurements, dataModel)
            const m2Overrun = getMetricResponseOverrun(m2[0], m2[1], report, measurements, dataModel)
            return m1Overrun.totalOverrun - m2Overrun.totalOverrun
        },
    }
    metrics.sort(sorters[sortColumn])
    if (sortDirection === "descending") {
        metrics.reverse()
    }
}

function subjectIsEmptyDueToFilters(atReportsOverview, filteredMetrics, metrics, settings) {
    // Hide the subject if it has no metrics after filtering and at least one of the following conditions holds:
    // - the user is at the reports overview page
    // - the user is hiding all metrics or metrics that don't require action
    // - the user is hiding metrics by tag
    // - the subject has metrics before filtering
    // This ensures (in combination with resetting the metricsToHide and hiddenTags settings after adding a subject)
    // that newly added subjects are not immediately hidden
    return (
        Object.keys(filteredMetrics).length === 0 &&
        (atReportsOverview ||
            !settings.metricsToHide.isDefault() ||
            !settings.hiddenTags.isDefault() ||
            Object.keys(metrics).length !== 0)
    )
}
subjectIsEmptyDueToFilters.propTypes = {
    atReportsOverview: bool,
    filteredMetrics: metricsPropType,
    metrics: metricsPropType,
    settings: settingsPropType,
}

export function Subject({
    atReportsOverview,
    changedFields,
    dates,
    firstSubject,
    handleSort,
    lastSubject,
    measurements,
    report,
    reportDate,
    reports,
    settings,
    subjectUuid,
    reload,
}) {
    const subject = report.subjects[subjectUuid]
    const metrics = visibleMetrics(subject.metrics, settings.metricsToHide.value, settings.hiddenTags.value)
    const dataModel = useContext(DataModel)
    if (subjectIsEmptyDueToFilters(atReportsOverview, metrics, subject.metrics, settings)) {
        return null
    }
    let metricEntries = Object.entries(metrics)
    if (settings.sortColumn.value !== "") {
        sortMetrics(
            dataModel,
            metricEntries,
            settings.sortDirection.value,
            settings.sortColumn.value,
            report,
            measurements,
        )
    }

    return (
        <Paper id={subjectUuid} elevation={5} sx={{ marginTop: "50px" }}>
            <SubjectTitle
                atReportsOverview={atReportsOverview}
                firstSubject={firstSubject}
                lastSubject={lastSubject}
                reload={reload}
                report={report}
                settings={settings}
                subject={subject}
                subjectUuid={subjectUuid}
            />
            <CommentSegment comment={subject.comment} />
            <Divider sx={{ padding: "0px" }} />
            <SubjectTable
                changedFields={changedFields}
                dates={dates}
                handleSort={handleSort}
                measurements={measurements}
                metricEntries={metricEntries}
                reload={reload}
                report={report}
                reportDate={reportDate}
                reports={reports}
                settings={settings}
                subject={subject}
                subjectUuid={subjectUuid}
            />
        </Paper>
    )
}
Subject.propTypes = {
    atReportsOverview: bool,
    changedFields: stringsPropType,
    dates: datesPropType,
    firstSubject: bool,
    handleSort: func,
    lastSubject: bool,
    measurements: measurementsPropType,
    report: reportPropType,
    reportDate: optionalDatePropType,
    reports: reportsPropType,
    settings: settingsPropType,
    subjectUuid: string,
    reload: func,
}
