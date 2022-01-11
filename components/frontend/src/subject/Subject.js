import React, { useContext, useEffect, useState } from 'react';
import { Dropdown } from 'semantic-ui-react';
import { DataModel } from '../context/DataModel';
import { get_subject_measurements } from '../api/subject';
import { get_metric_comment, get_metric_issue_ids, get_metric_name, get_metric_status, get_metric_tags, get_metric_target, getMetricUnit, get_metric_value, get_source_name } from '../utils';
import { TrendTable } from '../trend_table/TrendTable';
import { CommentSegment } from '../widgets/CommentSegment';
import { SubjectDetails } from './SubjectDetails';
import { SubjectTitle } from './SubjectTitle';

function HamburgerItems({ hideMetricsNotRequiringAction, subjectTrendTable, setHideMetricsNotRequiringAction, setSubjectTrendTable, }) {
    return (
        <>
            <Dropdown.Item key="view" onClick={() => setSubjectTrendTable(!subjectTrendTable)}>
                {subjectTrendTable ? "Show metric details" : "Show metric trend"}
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
            const attribute1 = get_metric_name(m1[1], datamodel);
            const attribute2 = get_metric_name(m2[1], datamodel);
            return attribute1.localeCompare(attribute2)
        },
        measurement: (m1, m2) => {
            const attribute1 = get_metric_value(m1[1]);
            const attribute2 = get_metric_value(m2[1]);
            return attribute1.localeCompare(attribute2)
        },
        target: (m1, m2) => {
            const attribute1 = get_metric_target(m1[1]);
            const attribute2 = get_metric_target(m2[1]);
            return attribute1.localeCompare(attribute2)
        },
        comment: (m1, m2) => {
            const attribute1 = get_metric_comment(m1[1]);
            const attribute2 = get_metric_comment(m2[1]);
            return attribute1.localeCompare(attribute2)
        },
        status: (m1, m2) => {
            const attribute1 = status_order[get_metric_status(m1[1])];
            const attribute2 = status_order[get_metric_status(m2[1])];
            return attribute1.localeCompare(attribute2)
        },
        source: (m1, m2) => {
            let m1_sources = Object.values(m1[1].sources).map((source) => get_source_name(source, datamodel));
            m1_sources.sort();
            let m2_sources = Object.values(m2[1].sources).map((source) => get_source_name(source, datamodel));
            m2_sources.sort();
            const attribute1 = m1_sources.length > 0 ? m1_sources[0] : '';
            const attribute2 = m2_sources.length > 0 ? m2_sources[0] : '';
            return attribute1.localeCompare(attribute2)
        },
        issues: (m1, m2) => {
            let m1_issues = get_metric_issue_ids(m1[1]);
            let m2_issues = get_metric_issue_ids(m2[1]);
            const attribute1 = m1_issues.length > 0 ? m1_issues[0] : '';
            const attribute2 = m2_issues.length > 0 ? m2_issues[0] : '';
            return attribute1.localeCompare(attribute2)
        },
        tags: (m1, m2) => {
            let m1_tags = get_metric_tags(m1[1]);
            let m2_tags = get_metric_tags(m2[1]);
            const attribute1 = m1_tags.length > 0 ? m1_tags[0] : '';
            const attribute2 = m2_tags.length > 0 ? m2_tags[0] : '';
            return attribute1.localeCompare(attribute2)
        },
        unit: (m1, m2) => {
            let attribute1 = getMetricUnit(m1[1], datamodel);
            let attribute2 = getMetricUnit(m2[1], datamodel);
            return attribute1.localeCompare(attribute2)
        }
    }
    metrics.sort(sorters[sortColumn]);
    if (sortDirection === 'descending') {
        metrics.reverse()
    }
}

export function Subject({
    changed_fields,
    first_subject,
    handleSort,
    hiddenColumns,
    hideMetricsNotRequiringAction,
    last_subject,
    report,
    report_date,
    reports,
    setHideMetricsNotRequiringAction,
    setSubjectTrendTable,
    setTrendTableInterval,
    setTrendTableNrDates,
    sortColumn,
    sortDirection,
    subject_uuid,
    subjectTrendTable,
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
        if (subjectTrendTable) {
            get_subject_measurements(subject_uuid, report_date).then(json => {
                if (json.ok !== false) {
                    setMeasurements(json.measurements)
                }
            })
        }
        // eslint-disable-next-line
    }, [subjectTrendTable]);

    let metricEntries = Object.entries(metrics);
    if (sortColumn !== null) {
        sortMetrics(dataModel, metricEntries, sortDirection, sortColumn);
    }

    const hamburgerItems = <HamburgerItems
        hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
        subjectTrendTable={subjectTrendTable}
        setSubjectTrendTable={setSubjectTrendTable}
        setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction}
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
            {subjectTrendTable ?
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
                :
                <SubjectDetails
                    changed_fields={changed_fields}
                    extraHamburgerItems={hamburgerItems}
                    handleSort={handleSort}
                    hiddenColumns={hiddenColumns}
                    metricEntries={metricEntries}
                    reload={reload}
                    report_date={report_date}
                    report={report}
                    reports={reports}
                    sortColumn={sortColumn}
                    sortDirection={sortDirection}
                    subject_uuid={subject_uuid}
                    toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                    toggleHiddenColumn={toggleHiddenColumn}
                    visibleDetailsTabs={visibleDetailsTabs}
                />
            }
        </div>
    )
}
