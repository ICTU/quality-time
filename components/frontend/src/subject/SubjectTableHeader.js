import { Table } from "semantic-ui-react";
import { SortableTableHeaderCell } from '../widgets/SortableTableHeaderCell';

export function SubjectTableHeader(
    {
        columnDates,
        handleSort,
        hiddenColumns,
        nrDates,
        sortColumn,
        sortDirection,
    }) {
    const sortProps = { sortColumn: sortColumn, sortDirection: sortDirection, handleSort: handleSort }
    return (
        <Table.Header>
            <Table.Row>
                <SortableTableHeaderCell colSpan="2" column='name' label='Metric' {...sortProps} />
                {nrDates > 1 && columnDates.map(date => <Table.HeaderCell key={date} className="unsortable" textAlign="right">{date.toLocaleDateString()}</Table.HeaderCell>)}
                {nrDates > 1 && <SortableTableHeaderCell column="unit" label="Unit" {...sortProps} />}
                {nrDates === 1 && !hiddenColumns.includes("trend") && <Table.HeaderCell className="unsortable" width="2">Trend (7 days)</Table.HeaderCell>}
                {nrDates === 1 && !hiddenColumns.includes("status") && <SortableTableHeaderCell column='status' label='Status' textAlign='center' {...sortProps} />}
                {nrDates === 1 && !hiddenColumns.includes("measurement") && <SortableTableHeaderCell column='measurement' label='Measurement' {...sortProps} />}
                {nrDates === 1 && !hiddenColumns.includes("target") && <SortableTableHeaderCell column='target' label='Target' {...sortProps} />}
                {!hiddenColumns.includes("source") && <SortableTableHeaderCell column='source' label='Source' {...sortProps} />}
                {!hiddenColumns.includes("comment") && <SortableTableHeaderCell column='comment' label='Comment' {...sortProps} />}
                {!hiddenColumns.includes("issues") && <SortableTableHeaderCell column='issues' label='Issues' {...sortProps} />}
                {!hiddenColumns.includes("tags") && <SortableTableHeaderCell column='tags' label='Tags' {...sortProps} />}
            </Table.Row>
        </Table.Header>
    )
}