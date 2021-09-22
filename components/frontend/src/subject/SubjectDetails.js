import React, { useState } from 'react';
import { Dropdown, Table } from 'semantic-ui-react';
import { Metric } from '../metric/Metric';
import { get_metric_comment, get_metric_issue_ids, get_metric_name, get_metric_status, get_metric_tags, get_metric_target, get_metric_value, get_source_name } from '../utils';
import { HamburgerMenu } from '../widgets/HamburgerMenu';
import { SubjectFooter } from './SubjectFooter';

function ColumnMenuItem({ column, hiddenColumns, toggleHiddenColumn }) {
    return (
        <Dropdown.Item onClick={() => toggleHiddenColumn(column)}>
            {hiddenColumns.includes(column) ? `Show ${column} column` : `Hide ${column} column`}
        </Dropdown.Item>
    )
}

function HamburgerHeader({ hiddenColumns, toggleHiddenColumn, extraHamburgerItems }) {
    return (
        <Table.HeaderCell collapsing textAlign="center">
            <HamburgerMenu>
                {extraHamburgerItems}
                <Dropdown.Header>Columns</Dropdown.Header>
                <ColumnMenuItem column="trend" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                <ColumnMenuItem column="status" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                <ColumnMenuItem column="measurement" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                <ColumnMenuItem column="target" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                <ColumnMenuItem column="source" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                <ColumnMenuItem column="comment" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                <ColumnMenuItem column="issues" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                <ColumnMenuItem column="tags" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
            </HamburgerMenu>
        </Table.HeaderCell>
    )
}

function SortableHeader({ column, sortColumn, sortDirection, handleSort, label, textAlign }) {
    const sorted = sortColumn === column ? sortDirection : null;
    return (
        <Table.HeaderCell onClick={() => handleSort(column)} sorted={sorted} textAlign={textAlign || 'left'}>
            {label}
        </Table.HeaderCell>
    )
}

function SubjectTableHeader({ hiddenColumns, toggleHiddenColumn, sortColumn, sortDirection, handleSort, extraHamburgerItems }) {
    const sortProps = { sortColumn: sortColumn, sortDirection: sortDirection, handleSort: handleSort }
    return (
        <Table.Header>
            <Table.Row>
                <HamburgerHeader hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} extraHamburgerItems={extraHamburgerItems} />
                <SortableHeader column='name' label='Metric' {...sortProps} />
                {!hiddenColumns.includes("trend") && <Table.HeaderCell width="2">Trend (7 days)</Table.HeaderCell>}
                {!hiddenColumns.includes("status") && <SortableHeader column='status' label='Status' textAlign='center' {...sortProps} />}
                {!hiddenColumns.includes("measurement") && <SortableHeader column='measurement' label='Measurement' {...sortProps} />}
                {!hiddenColumns.includes("target") && <SortableHeader column='target' label='Target' {...sortProps} />}
                {!hiddenColumns.includes("source") && <SortableHeader column='source' label='Source' {...sortProps} />}
                {!hiddenColumns.includes("comment") && <SortableHeader column='comment' label='Comment' {...sortProps} />}
                {!hiddenColumns.includes("issues") && <SortableHeader column='issues' label='Issues' {...sortProps} />}
                {!hiddenColumns.includes("tags") && <SortableHeader column='tags' label='Tags' {...sortProps} />}
            </Table.Row>
        </Table.Header>
    )
}

function createMetricComponents(
    datamodel,
    report,
    report_date,
    reports_overview,
    subject_uuid,
    metrics,
    changed_fields,
    visibleDetailsTabs,
    toggleVisibleDetailsTab,
    hiddenColumns,
    setSortColumn,
    reload) {
    const subject = report.subjects[subject_uuid];
    const last_index = Object.entries(subject.metrics).length - 1;

    let components = [];
    Object.entries(metrics).forEach(([metric_uuid, metric], index) => {
        components.push(
            <Metric
                datamodel={datamodel}
                reports_overview={reports_overview}
                report={report}
                report_date={report_date}
                subject_uuid={subject_uuid}
                metric={metric}
                metric_uuid={metric_uuid}
                first_metric={index === 0}
                last_metric={index === last_index}
                stop_sort={() => setSortColumn(null)}
                changed_fields={changed_fields}
                visibleDetailsTabs={visibleDetailsTabs}
                toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                hiddenColumns={hiddenColumns}
                key={metric_uuid}
                reload={reload}
            />)
    });
    return components
}

function sortMetricComponents(datamodel, metricComponents, sortDirection, sortColumn) {
    const status_order = { "": "0", target_not_met: "1", debt_target_met: "2", near_target_met: "3", target_met: "4" };
    const sorters = {
        name: (m1, m2) => {
            const attribute1 = get_metric_name(m1.props.metric, datamodel);
            const attribute2 = get_metric_name(m2.props.metric, datamodel);
            return attribute1.localeCompare(attribute2)
        },
        measurement: (m1, m2) => {
            const attribute1 = get_metric_value(m1.props.metric);
            const attribute2 = get_metric_value(m2.props.metric);
            return attribute1.localeCompare(attribute2)
        },
        target: (m1, m2) => {
            const attribute1 = get_metric_target(m1.props.metric);
            const attribute2 = get_metric_target(m2.props.metric);
            return attribute1.localeCompare(attribute2)
        },
        comment: (m1, m2) => {
            const attribute1 = get_metric_comment(m1.props.metric);
            const attribute2 = get_metric_comment(m2.props.metric);
            return attribute1.localeCompare(attribute2)
        },
        status: (m1, m2) => {
            const attribute1 = status_order[get_metric_status(m1.props.metric)];
            const attribute2 = status_order[get_metric_status(m2.props.metric)];
            return attribute1.localeCompare(attribute2)
        },
        source: (m1, m2) => {
            let m1_sources = Object.values(m1.props.metric.sources).map((source) => get_source_name(source, datamodel));
            m1_sources.sort();
            let m2_sources = Object.values(m2.props.metric.sources).map((source) => get_source_name(source, datamodel));
            m2_sources.sort();
            const attribute1 = m1_sources.length > 0 ? m1_sources[0] : '';
            const attribute2 = m2_sources.length > 0 ? m2_sources[0] : '';
            return attribute1.localeCompare(attribute2)
        },
        issues: (m1, m2) => {
            let m1_issues = get_metric_issue_ids(m1.props.metric);
            let m2_issues = get_metric_issue_ids(m2.props.metric);
            const attribute1 = m1_issues.length > 0 ? m1_issues[0] : '';
            const attribute2 = m2_issues.length > 0 ? m2_issues[0] : '';
            return attribute1.localeCompare(attribute2)
        },
        tags: (m1, m2) => {
            let m1_tags = get_metric_tags(m1.props.metric);
            let m2_tags = get_metric_tags(m2.props.metric);
            const attribute1 = m1_tags.length > 0 ? m1_tags[0] : '';
            const attribute2 = m2_tags.length > 0 ? m2_tags[0] : '';
            return attribute1.localeCompare(attribute2)
        }
    }
    metricComponents.sort(sorters[sortColumn]);
    if (sortDirection === 'descending') {
        metricComponents.reverse()
    }
}

export function SubjectDetails(props) {

    const [sortDirection, setSortDirection] = useState('ascending');
    const [sortColumn, setSortColumn] = useState(null);

    const metricComponents = createMetricComponents(props.datamodel, props.report, props.report_date, props.reports_overview, props.subject_uuid, props.metrics, props.changed_fields, props.visibleDetailsTabs, props.toggleVisibleDetailsTab, props.hiddenColumns, setSortColumn, props.reload)
    if (sortColumn !== null) {
        sortMetricComponents(props.datamodel, metricComponents, sortDirection, sortColumn)
    }

    function handleSort(column) {
        if (sortColumn === column) {
            if (sortDirection === 'descending') {
                setSortColumn(null)  // Cycle through ascending->descending->no sort as long as the user clicks the same column
            }
            setSortDirection(sortDirection === 'ascending' ? 'descending' : 'ascending')
        } else {
            setSortColumn(column)
        }
    }

    return (
        <>
            <SubjectTableHeader
                hiddenColumns={props.hiddenColumns}
                toggleHiddenColumn={props.toggleHiddenColumn}
                sortColumn={sortColumn}
                sortDirection={sortDirection}
                handleSort={handleSort}
                extraHamburgerItems={props.extraHamburgerItems} />
            <Table.Body>{metricComponents}</Table.Body>
            <SubjectFooter
                datamodel={props.datamodel}
                subjectUuid={props.subject_uuid}
                subject={props.report.subjects[props.subject_uuid]}
                reload={props.reload}
                reports={props.reports}
                resetSortColumn={() => { setSortColumn(null) }} />
        </>
    )
}
