import { Table } from "semantic-ui-react";
import { Label } from "../semantic_ui_react_wrappers";
import { SortableTableHeaderCell } from '../widgets/SortableTableHeaderCell';
import { StatusIcon } from '../measurement/StatusIcon';

const statusHelp = <>
    <p>
        The current status of the metric.
    </p>
    <p>
        Hover over the status to see how long the metric has had the current status.
    </p>
    <p>
        If the status is <StatusIcon status="informative" size="tiny" /> the measurement value is not evaluated against a target value.
    </p>
    <p>
        If the status is <StatusIcon status="target_met" size="tiny" /> the measurement value meets the target value.
    </p>
    <p>
        If the status is <StatusIcon status="near_target_met" size="tiny" /> the measurement value is close to the target value.
    </p>
    <p>
        If the status is <StatusIcon status="target_not_met" size="tiny" /> the measurement value does not meet the target value.
    </p>
    <p>
        If the status is <StatusIcon status="debt_target_met" size="tiny" /> the measurement value does not meet the target value,
        but this is accepted as technical debt. The measurement value does meet the technical debt target.
    </p>
    <p>
        If the status is <StatusIcon status="unknown" size="tiny" /> the status could not be determined because
        no sources have been configured for the metric yet or the measurement data could not be collected.
    </p>
</>

const measurementHelp = <>
    <p>
        The latest measurement value. Metrics are measured periodically.
    </p>
    <p>
        Hover over the measurement value to see when the metric was last measured.
    </p>
    <p>
        If the measurement value is '?', no sources have been configured for the metric yet or the measurement
        data could not be collected.
        Expand the metric and navigate to the sources tab to add sources or see the error details.
    </p>
    <p>
        If the measurement value has a <Label horizontal color="red">red background</Label>, the metric has not been measured recently.
        This indicates a problem with <em>Quality-time</em> itself, and a system administrator should be notified.
    </p>
</>

const timeLeftHelp = <>
    <p>
        The number of days left to address the metric.
    </p>
    <p>
        Hover of the number of days to see the exact deadline.
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
        Click a source to open the tool or report in a new tab.
    </p>
    <p>
        If a source has a <Label horizontal color="red">red background</Label>, the source could not be accessed or the
        data could not be parsed. Expand the metric and navigate to the source to see the error details.
    </p>
</>

const issuesHelp = <>
    <p>
        Links to issues, opened in an issue tracker such as Jira, to track progress of addressing the metric.
    </p>
    <p>
        Hover over an issue to see more information about the issue.
    </p>
    <p>
        Click an issue to open the issue in a new tab.
    </p>
    <p>
        If an issue has a <Label horizontal color="red">red background</Label>, the issue tracker could not be accessed
        or the data could not be parsed. Expand the metric and navigate to the technical debt tab to see the error details.
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
                {nrDates === 1 && !hiddenColumns.includes("status") && <SortableTableHeaderCell column='status' label='Status' textAlign='center' help={statusHelp} {...sortProps} />}
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