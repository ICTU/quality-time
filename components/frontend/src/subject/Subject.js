import React, { useEffect, useState } from 'react';
import { Dropdown } from 'semantic-ui-react';
import { get_subject_measurements } from '../api/subject';
import { TrendTable } from '../trend_table/TrendTable';
import { SubjectDetails } from './SubjectDetails';
import { SubjectTitle } from './SubjectTitle';

function HamburgerItems({ hideMetricsNotRequiringAction, subjectTrendTable, setHideMetricsNotRequiringAction, setSubjectTrendTable, }) {
    return (
        <>
            <Dropdown.Header>Views</Dropdown.Header>
            <Dropdown.Item onClick={() => setSubjectTrendTable(false)} active={!subjectTrendTable} >
                Details
            </Dropdown.Item>
            <Dropdown.Item onClick={() => setSubjectTrendTable(true)} active={subjectTrendTable} >
                Trend table
            </Dropdown.Item>
            <Dropdown.Header>Rows</Dropdown.Header>
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

export function Subject({
    changed_fields,
    datamodel,
    first_subject,
    hiddenColumns,
    hideMetricsNotRequiringAction,
    last_subject,
    report,
    report_date,
    reports,
    reports_overview,
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

    const hamburgerItems = <HamburgerItems
        hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
        subjectTrendTable={subjectTrendTable}
        setSubjectTrendTable={setSubjectTrendTable}
        setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction}
    />

    return (
        <div id={subject_uuid}>
            <SubjectTitle
                datamodel={datamodel}
                report={report}
                subject={subject}
                subject_uuid={subject_uuid}
                first_subject={first_subject}
                last_subject={last_subject}
                reload={reload} />
            {subjectTrendTable ?
                <TrendTable
                    changed_fields={changed_fields}
                    datamodel={datamodel}
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
                    reports_overview={reports_overview}
                    visibleDetailsTabs={visibleDetailsTabs}
                    toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                />
                :
                <SubjectDetails
                    changed_fields={changed_fields}
                    datamodel={datamodel}
                    hiddenColumns={hiddenColumns}
                    report={report}
                    reports={reports}
                    report_date={report_date}
                    reports_overview={reports_overview}
                    subject_uuid={subject_uuid}
                    metrics={metrics}
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
