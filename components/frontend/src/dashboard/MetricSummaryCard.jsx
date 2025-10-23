import { useTheme } from "@mui/material"
import { bool, func, number, object, oneOfType, string } from "prop-types"
import { VictoryContainer, VictoryLabel, VictoryTooltip } from "victory"

import { useBoundingBox } from "../hooks/boundingbox"
import { STATUSES } from "../metric/status"
import { pluralize, sum } from "../utils"
import { DashboardCard } from "./DashboardCard"
import { StatusBarChart } from "./StatusBarChart"
import { StatusPieChart } from "./StatusPieChart"

function nrMetricsLabel(nrMetrics) {
    return nrMetrics === 0 ? "No\nmetrics" : pluralize(`${nrMetrics}\nmetric`, nrMetrics)
}

function ariaChartLabel(summary) {
    let label = ""
    for (const [date, count] of Object.entries(summary)) {
        const nrMetrics = sum(count)
        const nrMetricsLabel = nrMetrics === 0 ? "no metrics" : pluralize(`${nrMetrics} metric`, nrMetrics)
        const dateString = new Date(date).toLocaleDateString()
        label += `Status on ${dateString}: ${nrMetricsLabel}`
        if (count.green > 0) {
            label += `, ${count.green} target met`
        }
        if (count.red > 0) {
            label += `, ${count.red} target not met`
        }
        if (count.yellow > 0) {
            label += `, ${count.yellow} near target`
        }
        if (count.grey > 0) {
            label += `, ${count.grey} with accepted technical debt`
        }
        if (count.blue > 0) {
            label += `, ${count.blue} informative`
        }
        if (count.white > 0) {
            label += `, ${count.white} with unknown status`
        }
        label += ". "
    }
    return label
}

export function MetricSummaryCard({ header, onClick, selected, summary, maxY }) {
    const [boundingBox, ref] = useBoundingBox()
    const animate = { duration: 0, onLoad: { duration: 0 } }
    const colors = STATUSES.map((status) => useTheme().palette[status].main)
    const bbWidth = boundingBox.width ?? 0
    const bbHeight = boundingBox.height ?? 0
    const tooltip = (
        <VictoryTooltip
            center={{ x: bbWidth / 2, y: bbHeight / 2 }}
            constrainToVisibleArea={true}
            cornerRadius={4}
            flyoutHeight={54} // If we don't pass this, a height is calculated by Victory, but it's much too high
            renderInPortal={false}
            style={{ fontFamily: "Arial", fontSize: 16 }}
        />
    )
    const dates = Object.keys(summary)
    const chartProps = {
        animate: animate,
        colors: colors,
        height: Math.max(bbHeight, 1), // Prevent "Failed prop type: Invalid prop range supplied to VictoryBar"
        label: (
            <VictoryLabel
                style={{ fill: useTheme().palette.text.secondary, fontFamily: useTheme().typography.fontFamily }}
                text={nrMetricsLabel(sum(summary[dates[0]]))}
                textAnchor="middle"
                x={bbWidth / 2}
                y={bbHeight / 2}
            />
        ),
        maxY: maxY,
        tooltip: tooltip,
        width: Math.max(bbWidth, 1), // Prevent "Failed prop type: Invalid prop range supplied to VictoryBar"
    }
    return (
        <DashboardCard onClick={onClick} selected={selected} title={header}>
            <div ref={ref}>
                <VictoryContainer aria-label={ariaChartLabel(summary)}>
                    {dates.length > 1 ? (
                        <StatusBarChart summary={summary} nrdates={dates.length} {...chartProps} />
                    ) : (
                        <StatusPieChart summary={summary[dates[0]]} {...chartProps} />
                    )}
                </VictoryContainer>
            </div>
        </DashboardCard>
    )
}
MetricSummaryCard.propTypes = {
    header: oneOfType([object, string]),
    onClick: func,
    selected: bool,
    summary: object,
    maxY: number,
}
