import React, { useContext } from 'react';
import PropTypes from 'prop-types';
import { DataModel } from '../context/DataModel';
import {
    datesPropType,
    optionalDatePropType,
    metricsPropType,
    reportPropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
} from '../sharedPropTypes';
import {
    get_metric_comment,
    getMetricIssueIds,
    get_metric_name,
    get_metric_status,
    getMetricTags,
    get_metric_target,
    getMetricResponseOverrun,
    getMetricResponseTimeLeft,
    getMetricUnit,
    get_metric_value,
    get_source_name,
    visibleMetrics
} from '../utils';
import { SubjectTable } from './SubjectTable';
import { CommentSegment } from '../widgets/CommentSegment';
import { SubjectTitle } from './SubjectTitle';
import './Subject.css'

function sortMetrics(datamodel, metrics, sortDirection, sortColumn, report, measurements) {
    const status_order = { "": "0", target_not_met: "1", near_target_met: "2", debt_target_met: "3", target_met: "4", informative: "5" };
    const sorters = {
        name: (m1, m2) => {
            const m1_name = get_metric_name(m1[1], datamodel);
            const m2_name = get_metric_name(m2[1], datamodel);
            return m1_name.localeCompare(m2_name)
        },
        measurement: (m1, m2) => {
            const m1_measurement = get_metric_value(m1[1]);
            const m2_measurement = get_metric_value(m2[1]);
            return m1_measurement.localeCompare(m2_measurement, undefined, { numeric: true })
        },
        target: (m1, m2) => {
            const m1_target = get_metric_target(m1[1]);
            const m2_target = get_metric_target(m2[1]);
            return m1_target.localeCompare(m2_target, undefined, { numeric: true })
        },
        comment: (m1, m2) => {
            const m1_comment = get_metric_comment(m1[1]);
            const m2_comment = get_metric_comment(m2[1]);
            return m1_comment.localeCompare(m2_comment)
        },
        status: (m1, m2) => {
            const m1_status = status_order[get_metric_status(m1[1])];
            const m2_status = status_order[get_metric_status(m2[1])];
            return m1_status.localeCompare(m2_status)
        },
        source: (m1, m2) => {
            let m1_sources = Object.values(m1[1].sources).map((source) => get_source_name(source, datamodel));
            m1_sources.sort();
            let m2_sources = Object.values(m2[1].sources).map((source) => get_source_name(source, datamodel));
            m2_sources.sort();
            return m1_sources.join().localeCompare(m2_sources.join())
        },
        issues: (m1, m2) => {
            const m1_issues = getMetricIssueIds(m1[1]).join();
            const m2_issues = getMetricIssueIds(m2[1]).join();
            return m1_issues.localeCompare(m2_issues)
        },
        tags: (m1, m2) => {
            const m1_tags = getMetricTags(m1[1]).join();
            const m2_tags = getMetricTags(m2[1]).join();
            return m1_tags.localeCompare(m2_tags)
        },
        unit: (m1, m2) => {
            const m1_unit = getMetricUnit(m1[1], datamodel);
            const m2_unit = getMetricUnit(m2[1], datamodel);
            return m1_unit.localeCompare(m2_unit)
        },
        time_left: (m1, m2) => {
            const m1_time_left = getMetricResponseTimeLeft(m1[1], report) ?? 0;
            const m2_time_left = getMetricResponseTimeLeft(m2[1], report) ?? 0;
            return m1_time_left - m2_time_left
        },
        overrun: (m1, m2) => {
            const m1_overrun = getMetricResponseOverrun(m1[0], m1[1], report, measurements);
            const m2_overrun = getMetricResponseOverrun(m2[0], m2[1], report, measurements);
            return m1_overrun.totalOverrun - m2_overrun.totalOverrun;
        }
    }
    metrics.sort(sorters[sortColumn]);
    if (sortDirection === 'descending') {
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
        Object.keys(filteredMetrics).length === 0 && (
            atReportsOverview ||
            !settings.metricsToHide.isDefault() ||
            !settings.hiddenTags.isDefault() ||
            Object.keys(metrics).length !== 0
        )
    )
}
subjectIsEmptyDueToFilters.propTypes = {
    atReportsOverview: PropTypes.bool,
    filteredMetrics: metricsPropType,
    metrics: metricsPropType,
    settings: settingsPropType,
}

export function Subject({
    atReportsOverview,
    changed_fields,
    dates,
    firstSubject,
    handleSort,
    lastSubject,
    measurements,
    report,
    report_date,
    reports,
    settings,
    subject_uuid,
    reload
}) {
    const subject = report.subjects[subject_uuid];
    const metrics = visibleMetrics(subject.metrics, settings.metricsToHide.value, settings.hiddenTags.value)
    const dataModel = useContext(DataModel)
    if (subjectIsEmptyDueToFilters(atReportsOverview, metrics, subject.metrics, settings)) {
        return null
    }
    let metricEntries = Object.entries(metrics);
    if (settings.sortColumn.value !== "") {
        sortMetrics(dataModel, metricEntries, settings.sortDirection.value, settings.sortColumn.value, report, measurements);
    }

    return (
        <div id={subject_uuid}>
            <div className="sticky">
                <SubjectTitle
                    atReportsOverview={atReportsOverview}
                    report={report}
                    subject={subject}
                    subject_uuid={subject_uuid}
                    firstSubject={firstSubject}
                    lastSubject={lastSubject}
                    reload={reload}
                />
            </div>
            <CommentSegment comment={subject.comment} />
            <SubjectTable
                changed_fields={changed_fields}
                dates={dates}
                handleSort={handleSort}
                measurements={measurements}
                metricEntries={metricEntries}
                reload={reload}
                report={report}
                reportDate={report_date}
                reports={reports}
                settings={settings}
                subject={subject}
                subject_uuid={subject_uuid}
            />
        </div>
    )
}
Subject.propTypes = {
    atReportsOverview: PropTypes.bool,
    changed_fields: stringsPropType,
    dates: datesPropType,
    firstSubject: PropTypes.bool,
    handleSort: PropTypes.func,
    lastSubject: PropTypes.bool,
    measurements: PropTypes.array,
    report: reportPropType,
    report_date: optionalDatePropType,
    reports: reportsPropType,
    settings: settingsPropType,
    subject_uuid: PropTypes.string,
    reload: PropTypes.func
}
