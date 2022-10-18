import { Table } from "semantic-ui-react";
import { Icon, Label } from "../semantic_ui_react_wrappers";
import { SortableTableHeaderCell, UnsortableTableHeaderCell } from '../widgets/TableHeaderCell';
import { StatusIcon } from '../measurement/StatusIcon';
import { HyperLink } from "../widgets/HyperLink";

const metricHelp = <>
    <p>
        The name of the metric.
    </p>
    <p>
        Expand the metric (click <Icon fitted name="triangle right" />) to edit its name in the configuration tab.
    </p>
    <p>
        Click the column header to sort the metrics by name.
    </p>
</>

const trendHelp = <>
    <p>
        The recent measurements of the metric displayed
        as <HyperLink url="https://en.wikipedia.org/wiki/Sparkline">sparkline graph</HyperLink>.
    </p>
    <p>
        If the sparkline graph is empty, either the metric has not been measured yet or the metric has the version
        number scale.
    </p>
    <p>
        Expand the metric (click  <Icon fitted name="triangle right" />) and navigate to the trend graph tab to see a
        graph of all measurements.
    </p>
</>

const statusHelp = <>
    <p>
        The current status of the metric.
    </p>
    <p>
        If the status is <StatusIcon status="informative" size="tiny" /> the measurement value is not evaluated against
        a target value.
    </p>
    <p>
        If the status is <StatusIcon status="target_met" size="tiny" /> the measurement value meets the target value.
    </p>
    <p>
        If the status is <StatusIcon status="near_target_met" size="tiny" /> the measurement value is close to the
        target value.
    </p>
    <p>
        If the status is <StatusIcon status="target_not_met" size="tiny" /> the measurement value does not meet the
        target value.
    </p>
    <p>
        If the status is <StatusIcon status="debt_target_met" size="tiny" /> the measurement value does not meet the
        target value, but this is accepted as <HyperLink url="https://en.wikipedia.org/wiki/Technical_debt">technical
        debt</HyperLink>. The measurement value does meet the technical debt target.
    </p>
    <p>
        If the status is <StatusIcon status="unknown" size="tiny" /> the status could not be determined because
        no sources have been configured for the metric yet or the measurement data could not be collected.
    </p>
    <p>
        Hover over the status to see how long the metric has had the current status.
    </p>
    <p>
        Click the column header to sort the metrics by status.
    </p>
</>

const measurementHelp = <>
    <p>
        The latest measurement value. Metrics are measured periodically.
    </p>
    <p>
        If the measurement value is '?', no sources have been configured for the metric yet or the measurement data
        could not be collected. Expand the metric (click <Icon fitted name="triangle right" />) and navigate to the
        sources tab to add sources or see the error details.
    </p>
    <p>
        If the measurement value has a <Label as="span" horizontal color="red">red background</Label>, the metric has
        not been measured recently. This indicates a problem with <em>Quality-time</em> itself, and a system
        administrator should be notified.
    </p>
    <p>
        Hover over the measurement value to see when the metric was last measured.
    </p>
    <p>
        Click the column header to sort the metrics by measurement value.
    </p>
</>

const targetHelp = <>
    <p>
        The value against which measurements are evaluated to determine whether a metric needs action.
    </p>
    <p>
        The target value has a <Label as="span" horizontal color="grey">grey background</Label> if the metric has
        accepted technical debt that is not applied because the technical debt end date is in the past or all issues
        linked to the metric have been resolved.
    </p>
    <p>
        Expand the metric (click <Icon fitted name="triangle right" />) to edit the target value in the configuration
        tab.
    </p>
    <p>
        Click the column header to sort the metrics by target value.
    </p>
</>

const unitHelp = <>
    <p>
        The <HyperLink url="https://en.wikipedia.org/wiki/Unit_of_measurement">unit</HyperLink> used for measurement and
        target values.
    </p>
    <p>
        Expand the metric (click <Icon fitted name="triangle right" />) to edit the unit name in the configuration tab.
    </p>
    <p>
        Click the column header to sort the metrics by unit.
    </p>
</>

const timeLeftHelp = <>
    <p>
        The number of days left to address the metric.
    </p>
    <p>
        If the metric needs action, the time left is based on the desired reaction times. Expand the report title
        (click <Icon fitted name="triangle right" />) to change the desired reaction times.
    </p>
    <p>
        If the metric has accepted technical debt, the time left is based on the technical debt end date. Expand the
        metric (click <Icon fitted name="triangle right" />) to edit technical debt end date in the technical debt tab.
     </p>
    <p>
        Hover the number of days to see the exact deadline.
    </p>
    <p>
        Click the column header to sort the metrics by time left.
    </p>
</>

const overrunHelp = <>
    <p>
        The amount of days the desired reaction time to address the metric was exceeded in the displayed period.
    </p>
    <p>
        Expand the report title (click <Icon fitted name="triangle right" />) to change the desired reaction times.
    </p>
    <p>
        Hover the number of days to see an overview of when and for which statuses the metric had overruns in the displayed period.
    </p>
    <p>
        Click the column header to sort the metrics by overrun.
    </p>
</>

const commentHelp = <>
    <p>
        Comments can be used to capture the rationale for accepting technical debt, or any other information.
        HTML and URLs are supported.
    </p>
    <p>
        Expand the metric (click <Icon fitted name="triangle right" />) to edit the comments.
    </p>
</>

const sourcesHelp = <>
    <p>
        The tools and reports accessed to collect the measurement data. One metric can have multiple sources.
    </p>
    <p>
        If a source has a <Label as="span" horizontal color="red">red background</Label>, the source could not be
        accessed or the data could not be parsed. Expand the metric (click <Icon fitted name="triangle right" />) and
        navigate to the source to see the error details.
    </p>
    <p>
        Expand the metric (click <Icon fitted name="triangle right" />) to configure sources.
    </p>
    <p>
        Click a source to open the tool or report in a new tab.
    </p>
    <p>
        Click the column header to sort the metrics by source.
    </p>
</>

const issuesHelp = <>
    <p>
        Links to issues, opened in an issue tracker such as Jira, to track progress of addressing the metric.
        One metric can have multiple issues linked to it.
    </p>
    <p>
        If an issue has a <Label as="span" horizontal color="red">red background</Label>, the issue tracker could not
        be accessed or the data could not be parsed. Expand the metric and navigate to the technical debt tab to see
        the error details.
    </p>
    <p>
        Hover over an issue to see more information about the issue.
    </p>
    <p>
        Click an issue to open the issue in a new tab.
    </p>
    <p>
        Click the column header to sort the metrics by issue identifier.
    </p>
</>

const tagsHelp = <>
    <p>
        Tags are arbitrary metric labels that can be used to group metrics. One metrics can have multiple tags.
    </p>
    <p>
        For each tag, a tag card is added to the report dashboard.
        Click on a tag card to show only metrics that have the selected tag.
        The selected tag turns blue to indicate it is filtered on.
        Click the selected tag again to turn off the filtering.
        Selecting multiple tags shows metrics that have at least one of the selected tags.
    </p>
    <p>
        Expand the metric (click <Icon fitted name="triangle right" />) to add or remove tags.
    </p>
    <p>
        Click the column header to sort the metrics by tag.
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
                <SortableTableHeaderCell colSpan="2" column='name' label='Metric' help={metricHelp} {...sortProps} />
                {nrDates > 1 && columnDates.map(date => <UnsortableTableHeaderCell key={date} textAlign="right" label={date.toLocaleDateString()} />)}
                {nrDates === 1 && !hiddenColumns.includes("trend") && <UnsortableTableHeaderCell width="2" label="Trend (7 days)" help={trendHelp} />}
                {nrDates === 1 && !hiddenColumns.includes("status") && <SortableTableHeaderCell column='status' label='Status' textAlign='center' help={statusHelp} {...sortProps} />}
                {nrDates === 1 && !hiddenColumns.includes("measurement") && <SortableTableHeaderCell column='measurement' label='Measurement' textAlign="right" help={measurementHelp} {...sortProps} />}
                {nrDates === 1 && !hiddenColumns.includes("target") && <SortableTableHeaderCell column='target' label='Target' textAlign="right" help={targetHelp} {...sortProps} />}
                {!hiddenColumns.includes("unit") && <SortableTableHeaderCell column="unit" label="Unit" help={unitHelp} {...sortProps} />}
                {!hiddenColumns.includes("source") && <SortableTableHeaderCell column='source' label='Sources' help={sourcesHelp} {...sortProps} />}
                {!hiddenColumns.includes("time_left") && <SortableTableHeaderCell column='time_left' label='Time left' help={timeLeftHelp} {...sortProps} />}
                {nrDates > 1 && !hiddenColumns.includes("overrun") && <SortableTableHeaderCell column='overrun' label='Overrun' help={overrunHelp} {...sortProps} />}
                {!hiddenColumns.includes("comment") && <SortableTableHeaderCell column='comment' label='Comment' help={commentHelp} {...sortProps} />}
                {!hiddenColumns.includes("issues") && <SortableTableHeaderCell column='issues' label='Issues' help={issuesHelp} {...sortProps} />}
                {!hiddenColumns.includes("tags") && <SortableTableHeaderCell column='tags' label='Tags' help={tagsHelp} {...sortProps} />}
            </Table.Row>
        </Table.Header>
    )
}