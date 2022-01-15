import React, { useContext, useEffect, useState } from 'react';
import { Dropdown } from 'semantic-ui-react';
import { DataModel } from '../context/DataModel';
import { get_subject_measurements } from '../api/subject';
import { get_metric_comment, get_metric_issue_ids, get_metric_name, get_metric_status, get_metric_tags, get_metric_target, getMetricUnit, get_metric_value, get_source_name } from '../utils';
import { TrendTable } from '../trend_table/TrendTable';
import { CommentSegment } from '../widgets/CommentSegment';
import { SubjectTitle } from './SubjectTitle';

function HamburgerItems({ clearVisibleDetailsTabs, hideMetricsNotRequiringAction, subjectTrendTable, setHideMetricsNotRequiringAction, setSubjectTrendTable, visibleDetailsTabs }) {
    return (
        <>
            <Dropdown.Item key="collapse_metrics" disabled={visibleDetailsTabs.length === 0} onClick={() => clearVisibleDetailsTabs()}>
                Collapse all metrics
            </Dropdown.Item>
            <Dropdown.Item onClick={() => setHideMetricsNotRequiringAction(!hideMetricsNotRequiringAction)}>
                {hideMetricsNotRequiringAction ? 'Show all metrics' : 'Hide metrics not requiring action'}
            </Dropdown.Item>
        </>
    )
}

function displayedMetrics(allMetrics, hideMetricsNotRequiringAction, tags) {
    const metrics = {}
    Object.entries(allMetrics).forEach(([metric_uuid, metric]) => {
        if (hideMetricsNotRequiringAction && (metric.status === "target_met" || metric.status === "debt_target_met")) { return }
        if (tags.length > 0 && tags.filter(value => metric.tags?.includes(value)).length === 0) { return }
        metrics[metric_uuid] = metric
    })
    return metrics
}

function sortMetrics(datamodel, metrics, sortDirection, sortColumn) {
    const status_order = { "": "0", target_not_met: "1", near_target_met: "2", debt_target_met: "3", target_met: "4" };
    const sorters = {
        name: (m1, m2) => {
            const m1_name = get_metric_name(m1[1], datamodel);
            const m2_name = get_metric_name(m2[1], datamodel);
            return m1_name.localeCompare(m2_name)
        },
        measurement: (m1, m2) => {
            const m1_measurement = get_metric_value(m1[1]);
            const m2_measurement = get_metric_value(m2[1]);
            return m1_measurement.localeCompare(m2_measurement)
        },
        target: (m1, m2) => {
            const m1_target = get_metric_target(m1[1]);
            const m2_target = get_metric_target(m2[1]);
            return m1_target.localeCompare(m2_target)
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
            const m1_tags = get_metric_tags(m1[1]).join();
            const m2_tags = get_metric_tags(m2[1]).join();
            return m1_tags.localeCompare(m2_tags)
        },
        unit: (m1, m2) => {
            const m1_unit = getMetricUnit(m1[1], datamodel);
            const m2_unit = getMetricUnit(m2[1], datamodel);
            return m1_unit.localeCompare(m2_unit)
        }
    }
    metrics.sort(sorters[sortColumn]);
    if (sortDirection === 'descending') {
        metrics.reverse()
    }
}

export function Subject({
    changed_fields,
    clearVisibleDetailsTabs,
    first_subject,
    handleSort,
    hiddenColumns,
    hideMetricsNotRequiringAction,
    last_subject,
    report,
    report_date,
    reports,
    setHideMetricsNotRequiringAction,
    setTrendTableInterval,
    setTrendTableNrDates,
    sortColumn,
    sortDirection,
    subject_uuid,
    tags,
    toggleHiddenColumn,
    toggleVisibleDetailsTab,
    trendTableInterval,
    trendTableNrDates,
    visibleDetailsTabs,
    reload
}) {
    const subject = report.subjects[subject_uuid];
    const metrics = displayedMetrics(subject.metrics, hideMetricsNotRequiringAction, tags)

    const [measurements, setMeasurements] = useState([]);
    const dataModel = useContext(DataModel)

    useEffect(() => {
        if (trendTableNrDates > 1) {
            get_subject_measurements(subject_uuid, report_date).then(json => {
                if (json.ok !== false) {
                    setMeasurements(json.measurements)
                }
            })
        }
        // eslint-disable-next-line
    }, [trendTableNrDates]);

    let metricEntries = Object.entries(metrics);
    if (sortColumn !== null) {
        sortMetrics(dataModel, metricEntries, sortDirection, sortColumn);
    }

    const hamburgerItems = <HamburgerItems
        clearVisibleDetailsTabs={clearVisibleDetailsTabs}
        hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
        setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction}
        visibleDetailsTabs={visibleDetailsTabs}
    />

    return (
        <div id={subject_uuid}>
            <SubjectTitle
                report={report}
                subject={subject}
                subject_uuid={subject_uuid}
                first_subject={first_subject}
                last_subject={last_subject}
                reload={reload} />
            <CommentSegment comment={subject.comment} />
            <TrendTable
                changed_fields={changed_fields}
                extraHamburgerItems={hamburgerItems}
                handleSort={handleSort}
                hiddenColumns={hiddenColumns}
                measurements={measurements}
                metricEntries={metricEntries}
                reload={reload}
                report={report}
                reportDate={report_date}
                reports={reports}
                setTrendTableInterval={setTrendTableInterval}
                setTrendTableNrDates={setTrendTableNrDates}
                sortDirection={sortDirection}
                sortColumn={sortColumn}
                subject={subject}
                subject_uuid={subject_uuid}
                toggleHiddenColumn={toggleHiddenColumn}
                toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                trendTableInterval={trendTableInterval}
                trendTableNrDates={trendTableNrDates}
                visibleDetailsTabs={visibleDetailsTabs}
            />
        </div>
    )
}
