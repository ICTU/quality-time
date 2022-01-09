import React, { useContext, useState } from 'react';
import { Dropdown, Icon, Table } from 'semantic-ui-react';
import { DataModel } from '../context/DataModel';
import { Metric } from '../metric/Metric';
import { get_metric_comment, get_metric_issue_ids, get_metric_name, get_metric_status, get_metric_tags, get_metric_target, get_metric_value, get_source_name } from '../utils';
import { ColumnMenuItem, HamburgerMenu } from '../widgets/HamburgerMenu';
import { SubjectFooter } from './SubjectFooter';

function HamburgerHeader({ hiddenColumns, toggleHiddenColumn, extraHamburgerItems }) {
    return (
        <Table.HeaderCell textAlign="center">
            <HamburgerMenu>
                {extraHamburgerItems}
                <Dropdown.Item key="columns">
                    <Icon name='dropdown' /><span className='text'>Toggle visibility of columns</span>
                    <Dropdown.Menu>
                        <ColumnMenuItem column="trend" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                        <ColumnMenuItem column="status" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                        <ColumnMenuItem column="measurement" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                        <ColumnMenuItem column="target" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                        <ColumnMenuItem column="source" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                        <ColumnMenuItem column="comment" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                        <ColumnMenuItem column="issues" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                        <ColumnMenuItem column="tags" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                    </Dropdown.Menu>
                </Dropdown.Item>
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

export function SubjectDetails({
    report,
    reports,
    report_date,
    subject_uuid,
    metrics,
    changed_fields,
    sortColumn,
    setSortColumn,
    sortDirection,
    setSortDirection,
    visibleDetailsTabs,
    toggleVisibleDetailsTab,
    hiddenColumns,
    toggleHiddenColumn,
    extraHamburgerItems,
    reload
}) {
    const dataModel = useContext(DataModel)

    let metricEntries = Object.entries(metrics);
    if (sortColumn !== null) {
        sortMetrics(dataModel, metricEntries, sortDirection, sortColumn);
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
    const subject = report.subjects[subject_uuid];
    const last_index = Object.entries(subject.metrics).length - 1;

    return (
        <Table sortable>
            <SubjectTableHeader
                hiddenColumns={hiddenColumns}
                toggleHiddenColumn={toggleHiddenColumn}
                sortColumn={sortColumn}
                sortDirection={sortDirection}
                handleSort={handleSort}
                extraHamburgerItems={extraHamburgerItems} />
            <Table.Body>
                {metricEntries.map(([metric_uuid, metric], index) =>
                    <Metric
                        reports={reports}
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
                    />)}
            </Table.Body>
            <SubjectFooter
                subjectUuid={subject_uuid}
                subject={report.subjects[subject_uuid]}
                reload={reload}
                reports={reports}
                resetSortColumn={() => { setSortColumn(null) }} />
        </Table>
    )
}
