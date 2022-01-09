import React from 'react';
import { Dropdown, Icon, Table } from 'semantic-ui-react';
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

export function SubjectDetails({
    report,
    reports,
    report_date,
    subject_uuid,
    metricEntries,
    changed_fields,
    handleSort,
    sortColumn,
    sortDirection,
    visibleDetailsTabs,
    toggleVisibleDetailsTab,
    hiddenColumns,
    toggleHiddenColumn,
    extraHamburgerItems,
    reload
}) {
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
                        stop_sort={() => handleSort(null)}
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
                resetSortColumn={() => { handleSort(null) }} />
        </Table>
    )
}
