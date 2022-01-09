import React, { useContext, useEffect, useState } from 'react';
import { Dropdown } from 'semantic-ui-react';
import { DataModel } from '../context/DataModel';
import { get_subject_measurements } from '../api/subject';
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

    const [sortColumn, setSortColumn] = useState(null);
    const [sortDirection, setSortDirection] = useState('ascending');
    const [measurements, setMeasurements] = useState([]);

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

    function handleSort(column) {
        if (sortColumn === null) {
            setSortColumn(null)  // Stop sorting
            return
        }
        if (sortColumn === column) {
            if (sortDirection === 'descending') {
                setSortColumn(null)  // Cycle through ascending->descending->no sort as long as the user clicks the same column
            }
            setSortDirection(sortDirection === 'ascending' ? 'descending' : 'ascending')
        } else {
            setSortColumn(column)
        }
    }

    const dataModel = useContext(DataModel)

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
                    hiddenColumns={hiddenColumns}
                    toggleHiddenColumn={toggleHiddenColumn}
                    reportDate={report_date}
                    metrics={metrics}
                    measurements={measurements}
                    extraHamburgerItems={hamburgerItems}
                    trendTableInterval={trendTableInterval}
                    setTrendTableInterval={setTrendTableInterval}
                    trendTableNrDates={trendTableNrDates}
                    setTrendTableNrDates={setTrendTableNrDates}
                    subject_uuid={subject_uuid}
                    subject={subject}
                    reload={reload}
                    report={report}
                    reports={reports}
                    visibleDetailsTabs={visibleDetailsTabs}
                    toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                />
                :
                <SubjectDetails
                    changed_fields={changed_fields}
                    hiddenColumns={hiddenColumns}
                    report={report}
                    reports={reports}
                    report_date={report_date}
                    subject_uuid={subject_uuid}
                    metricEntries={metricEntries}
                    sortColumn={sortColumn}
                    sortDirection={sortDirection}
                    handleSort={(column) => handleSort(column)}
                    visibleDetailsTabs={visibleDetailsTabs}
                    toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                    toggleHiddenColumn={toggleHiddenColumn}
                    extraHamburgerItems={hamburgerItems}
                    reload={reload}
                />
            }
        </div>
    )
}
