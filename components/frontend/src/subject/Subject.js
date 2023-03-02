import React, { useContext } from 'react';
import { DataModel } from '../context/DataModel';
import { get_metric_comment, get_metric_issue_ids, get_metric_name, get_metric_status, getMetricTags, get_metric_target, getMetricResponseOverrun, getMetricResponseTimeLeft, getMetricUnit, get_metric_value, get_source_name } from '../utils';
import { SubjectTable } from './SubjectTable';
import { CommentSegment } from '../widgets/CommentSegment';
import { SubjectTitle } from './SubjectTitle';
import './Subject.css'

function displayedMetrics(allMetrics, hideMetricsNotRequiringAction, tags) {
    const metrics = {}
    Object.entries(allMetrics).forEach(([metric_uuid, metric]) => {
        if (hideMetricsNotRequiringAction && (["target_met", "debt_target_met", "informative"].includes(metric.status))) { return }
        if (tags.length > 0 && tags.filter(value => metric.tags?.includes(value)).length === 0) { return }
        metrics[metric_uuid] = metric
    })
    return metrics
}

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
            return m1_measurement.localeCompare(m2_measurement, undefined, {numeric: true})
        },
        target: (m1, m2) => {
            const m1_target = get_metric_target(m1[1]);
            const m2_target = get_metric_target(m2[1]);
            return m1_target.localeCompare(m2_target, undefined, {numeric: true})
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
            const m1_issues = get_metric_issue_ids(m1[1]).join();
            const m2_issues = get_metric_issue_ids(m2[1]).join();
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

export function Subject({
    changed_fields,
    dates,
    first_subject,
    handleSort,
    hiddenColumns,
    hideMetricsNotRequiringAction,
    issueSettings,
    last_subject,
    measurements,
    report,
    report_date,
    reports,
    sortColumn,
    sortDirection,
    subject_uuid,
    tags,
    toggleVisibleDetailsTab,
    visibleDetailsTabs,
    reload
}) {
    const subject = report.subjects[subject_uuid];
    const metrics = displayedMetrics(subject.metrics, hideMetricsNotRequiringAction, tags)
    const dataModel = useContext(DataModel)
    let metricEntries = Object.entries(metrics);
    if (sortColumn !== null) {
        sortMetrics(dataModel, metricEntries, sortDirection, sortColumn, report, measurements);
    }

    return (
        <div id={subject_uuid}>
            <div className="sticky">
                <SubjectTitle
                    report={report}
                    subject={subject}
                    subject_uuid={subject_uuid}
                    first_subject={first_subject}
                    last_subject={last_subject}
                    reload={reload}
                />
            </div>
            <CommentSegment comment={subject.comment} />
            <SubjectTable
                changed_fields={changed_fields}
                dates={dates}
                handleSort={handleSort}
                hiddenColumns={hiddenColumns}
                issueSettings={issueSettings}
                measurements={measurements}
                metricEntries={metricEntries}
                reload={reload}
                report={report}
                reportDate={report_date}
                reports={reports}
                sortDirection={sortDirection}
                sortColumn={sortColumn}
                subject={subject}
                subject_uuid={subject_uuid}
                toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                visibleDetailsTabs={visibleDetailsTabs}
            />
        </div>
    )
}
