import { Chip, List, ListItem, ListItemIcon, ListItemText, Paper, TableHead, TableRow, Typography } from "@mui/material"
import { bool, func, string } from "prop-types"

import { zIndexTableHeader } from "../defaults"
import { StatusIcon } from "../measurement/StatusIcon"
import { STATUS_DESCRIPTION, STATUSES } from "../metric/status"
import { datesPropType, settingsPropType, stringsPropType } from "../sharedPropTypes"
import { HyperLink } from "../widgets/HyperLink"
import { IgnoreIcon, TriangleRightIcon } from "../widgets/icons"
import { SortableTableHeaderCell, UnsortableTableHeaderCell } from "../widgets/TableHeaderCell"

function Expand({ children }) {
    return (
        <>
            Expand the {children} (click
            <TriangleRightIcon />)
        </>
    )
}
Expand.propTypes = {
    children: string,
}

const metricHelp = (
    <>
        <p>The name of the metric.</p>
        <p>
            <Expand>metric</Expand> to edit its name in the configuration tab.
        </p>
        <p>Click the column header to sort the metrics by name.</p>
    </>
)

const trendHelp = (
    <>
        <p>
            The recent measurements of the metric displayed as{" "}
            <HyperLink url="https://en.wikipedia.org/wiki/Sparkline">sparkline graph</HyperLink>.
        </p>
        <p>
            If the sparkline graph is empty, either the metric has not been measured yet or the metric has the version
            number scale.
        </p>
        <p>
            <Expand>metric</Expand> and navigate to the trend graph tab to see a graph of all measurements.
        </p>
    </>
)

function statusHelp() {
    return (
        <>
            <p>The current status of the metric.</p>
            <List>
                {STATUSES.map((status) => (
                    <ListItem key={status} alignItems="flex-start">
                        <ListItemIcon>
                            <StatusIcon status={status} />
                        </ListItemIcon>
                        <ListItemText disableTypography>{STATUS_DESCRIPTION[status]}</ListItemText>
                    </ListItem>
                ))}
            </List>
            <p>Hover over the status to see how long the metric has had the current status.</p>
            <p>Click the column header to sort the metrics by status.</p>
        </>
    )
}

const measurementHelp = (
    <>
        <p>The latest measurement value. Metrics are measured periodically.</p>
        <p>
            If the measurement value is ?, no sources have been configured for the metric yet or the measurement data
            could not be collected. <Expand>metric</Expand> and navigate to the sources tab to add sources or see the
            error details.
        </p>
        <p>
            If the measurement value has a{" "}
            <Typography component="span" display="inline" bgcolor="error.main">
                red background
            </Typography>
            , the metric has not been measured recently. This indicates a problem with <em>Quality-time</em> itself, and
            a system administrator should be notified.
        </p>
        <p>
            If there is a <IgnoreIcon /> before the measurement value, it means one or more measurement entities are
            being ignored. Hover over the measurement value to see how many entities are ignored.{" "}
            <Expand>metric</Expand> and navigate to the entities tab to see why individual entities are ignored.
        </p>
        <p>Hover over the measurement value to see when the metric was last measured.</p>
        <p>Click the column header to sort the metrics by measurement value.</p>
    </>
)

const targetHelp = (
    <>
        <p>The value against which measurements are evaluated to determine whether a metric needs action.</p>
        <p>
            The target value has a{" "}
            <Typography component="span" display="inline" bgcolor="grey">
                grey background
            </Typography>{" "}
            if the metric has accepted technical debt that is not applied because the technical debt end date is in the
            past or all issues linked to the metric have been resolved.
        </p>
        <p>
            <Expand>metric</Expand> to edit the target value in the configuration tab.
        </p>
        <p>Click the column header to sort the metrics by target value.</p>
    </>
)

const unitHelp = (
    <>
        <p>
            The <HyperLink url="https://en.wikipedia.org/wiki/Unit_of_measurement">unit</HyperLink> used for measurement
            and target values.
        </p>
        <p>
            <Expand>metric</Expand> to edit the unit name in the configuration tab.
        </p>
        <p>Click the column header to sort the metrics by unit.</p>
    </>
)

const timeLeftHelp = (
    <>
        <p>The number of days left to address the metric.</p>
        <p>
            If the metric needs action, the time left is based on the desired reaction times.{" "}
            <Expand>report title</Expand> to change the desired reaction times.
        </p>
        <p>
            If the metric has accepted technical debt, the time left is based on the technical debt end date.{" "}
            <Expand>metric</Expand> to edit technical debt end date in the technical debt tab.
        </p>
        <p>Hover over the number of days to see the exact deadline.</p>
        <p>Click the column header to sort the metrics by time left.</p>
    </>
)

const overrunHelp = (
    <>
        <p>The number of days that the desired reaction time was exceeded, in the displayed period.</p>
        <p>
            <Expand>report title</Expand> to change the desired reaction times.
        </p>
        <p>
            Hover over the number of days to see an overview of when and for which statuses the metric had overruns, in
            the displayed period.
        </p>
        <p>Click the column header to sort the metrics by the number of days overrun.</p>
    </>
)

const commentHelp = (
    <>
        <p>
            Comments can be used to capture the rationale for accepting technical debt, or any other information. HTML
            and URLs are supported.
        </p>
        <p>
            <Expand>metric</Expand> to edit the comments.
        </p>
    </>
)

const sourcesHelp = (
    <>
        <p>The tools and reports accessed to collect the measurement data. One metric can have multiple sources.</p>
        <p>
            If a source has a{" "}
            <Typography component="span" display="inline" bgcolor="error.main">
                red background
            </Typography>
            , the source could not be accessed or the data could not be parsed. <Expand>metric</Expand> and navigate to
            the source to see the error details.
        </p>
        <p>
            <Expand>metric</Expand> to configure sources.
        </p>
        <p>Click a source to open the tool or report in a new tab.</p>
        <p>Click the column header to sort the metrics by source.</p>
    </>
)

const issuesHelp = (
    <>
        <p>
            Links to issues, opened in an issue tracker such as Jira, to track progress of addressing the metric. One
            metric can have multiple issues linked to it.
        </p>
        <p>
            If an issue has a{" "}
            <Typography component="span" display="inline" bgcolor="error.main">
                red background
            </Typography>
            , the issue tracker could not be accessed or the data could not be parsed. <Expand>metric</Expand> and
            navigate to the technical debt tab to see the error details.
        </p>
        <p>Hover over an issue to see more information about the issue.</p>
        <p>Click an issue to open the issue in a new tab.</p>
        <p>Click the column header to sort the metrics by issue identifier.</p>
    </>
)

const tagsHelp = (
    <>
        <p>Tags are arbitrary metric labels that can be used to group metrics. One metrics can have multiple tags.</p>
        <p>
            For each tag, a tag card is added to the report dashboard. Click on a tag card to show only metrics that
            have the selected tag. The selected tag turns blue to indicate it is filtered on. Click the selected tag
            again to turn off the filtering. Selecting multiple tags shows metrics that have at least one of the
            selected tags.
        </p>
        <p>
            <Expand>metric</Expand> to add or remove tags.
        </p>
        <p>Click the column header to sort the metrics by tag.</p>
    </>
)

function InlineChip({ color, label }) {
    return (
        <Paper
            component="span" // Default component is div Use span to prevent "Warning: validateDOMNesting(...): <div> cannot appear as a descendant of <p>."
            elevation={0}
            sx={{ display: "inline-flex" }}
        >
            <Chip
                color={color}
                component="span" // Default component is div Use span to prevent "Warning: validateDOMNesting(...): <div> cannot appear as a descendant of <p>."
                label={label}
                size="small"
                sx={{ borderRadius: 1 }}
                variant="outlined"
            />
        </Paper>
    )
}
InlineChip.propTypes = {
    color: string,
    label: string,
}

function MeasurementHeaderCells({ columnDates, showDeltaColumns }) {
    const cells = []
    columnDates.forEach((date, index) => {
        if (showDeltaColumns && index > 0) {
            cells.push(
                <UnsortableTableHeaderCell
                    key={`delta-${date}`}
                    help={
                        <>
                            <p>
                                The delta (𝚫) column shows the difference between the measurement values on the previous
                                and next date.
                            </p>
                            <p>
                                A plus sign <InlineChip color="info" label="+" /> indicates that the newer value is
                                higher. A minus sign <InlineChip color="info" label="+" /> indicates that the newer
                                value is lower.
                            </p>
                            <p>
                                A <InlineChip color="success" label="green outline" />
                                indicates that the newer value is better. A{" "}
                                <InlineChip color="error" label="red outline" />
                                indicates that the newer value is worse. A{" "}
                                <InlineChip color="info" label="blue outline" />
                                is used for metrics that are informative.
                            </p>
                            <p>
                                Note: if the value on the previous date is unknown, the value on the next date is
                                compared with the most recent known value.
                            </p>
                        </>
                    }
                    label="𝚫"
                    textAlign="right"
                />,
            )
        }
        cells.push(<UnsortableTableHeaderCell key={date} textAlign="right" label={date.toLocaleDateString()} />)
    })
    return cells
}
MeasurementHeaderCells.propTypes = {
    columnDates: datesPropType,
    showDeltaColumns: bool,
}

export function SubjectTableHeader({ columnDates, columnsToHide, handleSort, settings }) {
    const sortProps = {
        sortColumn: settings.sortColumn.value,
        sortDirection: settings.sortDirection,
        handleSort: handleSort,
    }
    const nrDates = columnDates.length
    return (
        <TableHead sx={{ bgcolor: "background.default", zIndex: zIndexTableHeader }}>
            <TableRow>
                <SortableTableHeaderCell column="name" label="Metric" help={metricHelp} {...sortProps} />
                {nrDates > 1 && (
                    <MeasurementHeaderCells
                        columnDates={columnDates}
                        showDeltaColumns={!columnsToHide.includes("delta")}
                    />
                )}
                {!columnsToHide.includes("trend") && (
                    <UnsortableTableHeaderCell width="2" label="Trend (7 days)" help={trendHelp} />
                )}
                {!columnsToHide.includes("status") && (
                    <SortableTableHeaderCell column="status" label="Status" help={statusHelp()} {...sortProps} />
                )}
                {!columnsToHide.includes("measurement") && (
                    <SortableTableHeaderCell
                        column="measurement"
                        label="Measurement"
                        textAlign="right"
                        help={measurementHelp}
                        {...sortProps}
                    />
                )}
                {!columnsToHide.includes("target") && (
                    <SortableTableHeaderCell
                        column="target"
                        label="Target"
                        textAlign="right"
                        help={targetHelp}
                        {...sortProps}
                    />
                )}
                {!columnsToHide.includes("unit") && (
                    <SortableTableHeaderCell column="unit" label="Unit" help={unitHelp} {...sortProps} />
                )}
                {!columnsToHide.includes("source") && (
                    <SortableTableHeaderCell column="source" label="Sources" help={sourcesHelp} {...sortProps} />
                )}
                {!columnsToHide.includes("time_left") && (
                    <SortableTableHeaderCell column="time_left" label="Time left" help={timeLeftHelp} {...sortProps} />
                )}
                {!columnsToHide.includes("overrun") && (
                    <SortableTableHeaderCell column="overrun" label="Overrun" help={overrunHelp} {...sortProps} />
                )}
                {!columnsToHide.includes("comment") && (
                    <SortableTableHeaderCell column="comment" label="Comment" help={commentHelp} {...sortProps} />
                )}
                {!columnsToHide.includes("issues") && (
                    <SortableTableHeaderCell column="issues" label="Issues" help={issuesHelp} {...sortProps} />
                )}
                {!columnsToHide.includes("tags") && (
                    <SortableTableHeaderCell column="tags" label="Tags" help={tagsHelp} {...sortProps} />
                )}
            </TableRow>
        </TableHead>
    )
}
SubjectTableHeader.propTypes = {
    columnDates: datesPropType,
    columnsToHide: stringsPropType,
    handleSort: func,
    settings: settingsPropType,
}
