import { Table } from "semantic-ui-react";
import { SortableTableHeaderCell } from '../widgets/SortableTableHeaderCell';

const measurementHelp = <>
    <p>
        The latest measurement value.
    </p>
    <p>
        If the measurement value is '?', no sources have been configured for the metric.
        Expand the metric and navigate to the sources tab to add sources.
    </p>
    <p>
        If the measurement value has a red background, the metric has not been measured recently.
    </p>
</>

const timeLeftHelp = <>
    <p>
        The number of days left to address the metric.
    </p>
    <p>
        If the metric needs action, the time left is based on the desired reaction times.
        The desired reaction times can be changed in the report header.</p>
    <p>
        If the metric has accepted technical debt, the time left is based on the technical debt end date.
    </p>
</>

const sourcesHelp = <>
    <p>
        The tools and reports accessed to collect the measurement data.
    </p>
    <p>
        If a source has a red background, the source could not be accessed or the data could not be parsed.
        Expand the metric and navigate to the source to see the error details.
    </p>
</>

const issuesHelp = <>
    <p>
        Links to issues, opened in an issue tracker such as Jira, to track progress of addressing the metric.
    </p>
    <p>
        If an issue has a red background, the issue tracker could not be accessed or the data could not be parsed.
        Expand the metric and navigate to the technical debt tab to see the error details.
    </p>
</>

export function SubjectTableHeader(
    {
        columnDates,
        handleSort,
        hiddenColumns,
        sortColumn,
        sortDirection,
    }) {
    const sortProps = { sortColumn: sortColumn, sortDirection: sortDirection, handleSort: handleSort }
    const nrDates = columnDates.length
    return (
        <Table.Header>
            <Table.Row>
                <SortableTableHeaderCell colSpan="2" column='name' label='Metric' {...sortProps} />
                {nrDates > 1 && columnDates.map(date => <Table.HeaderCell key={date} className="unsortable" textAlign="right">{date.toLocaleDateString()}</Table.HeaderCell>)}
                {nrDates === 1 && !hiddenColumns.includes("trend") && <Table.HeaderCell className="unsortable" width="2">Trend (7 days)</Table.HeaderCell>}
                {nrDates === 1 && !hiddenColumns.includes("status") && <SortableTableHeaderCell column='status' label='Status' textAlign='center' {...sortProps} />}
                {nrDates === 1 && !hiddenColumns.includes("measurement") && <SortableTableHeaderCell column='measurement' label='Measurement' textAlign="right" help={measurementHelp} {...sortProps} />}
                {nrDates === 1 && !hiddenColumns.includes("target") && <SortableTableHeaderCell column='target' label='Target' textAlign="right" {...sortProps} />}
                {!hiddenColumns.includes("unit") && <SortableTableHeaderCell column="unit" label="Unit" {...sortProps} />}
                {!hiddenColumns.includes("source") && <SortableTableHeaderCell column='source' label='Sources' help={sourcesHelp} {...sortProps} />}
                {!hiddenColumns.includes("time_left") && <SortableTableHeaderCell column='time_left' label='Time left' help={timeLeftHelp} {...sortProps} />}
                {!hiddenColumns.includes("comment") && <SortableTableHeaderCell column='comment' label='Comment' {...sortProps} />}
                {!hiddenColumns.includes("issues") && <SortableTableHeaderCell column='issues' label='Issues' help={issuesHelp} {...sortProps} />}
                {!hiddenColumns.includes("tags") && <SortableTableHeaderCell column='tags' label='Tags' {...sortProps} />}
            </Table.Row>
        </Table.Header>
    )
}