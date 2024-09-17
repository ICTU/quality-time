import "./MetricSummaryCard.css"

import { bool, func, number, object, oneOfType, string } from "prop-types"
import { useContext } from "react"
import { VictoryContainer, VictoryLabel, VictoryPortal, VictoryTooltip } from "victory"

import { DarkMode } from "../context/DarkMode"
import { useBoundingBox } from "../hooks/boundingbox"
import { STATUS_COLORS_RGB, STATUSES } from "../metric/status"
import { pluralize, sum } from "../utils"
import { DashboardCard } from "./DashboardCard"
import { StatusBarChart } from "./StatusBarChart"
import { StatusPieChart } from "./StatusPieChart"

function nrMetricsLabel(nrMetrics) {
    return nrMetrics === 0 ? "No\nmetrics" : pluralize(`${nrMetrics}\nmetric`, nrMetrics)
}

function ariaChartLabel(summary) {
    let label = ""
    Object.entries(summary).forEach(([date, count]) => {
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
    })
    return label
}

export function MetricSummaryCard({ header, onClick, selected, summary, maxY }) {
    const [boundingBox, ref] = useBoundingBox()
    const labelColor = useContext(DarkMode) ? "darkgrey" : "rgba(120, 120, 120)"
    const flyoutBgColor = useContext(DarkMode) ? "rgba(60, 65, 70)" : "white"
    const animate = { duration: 0, onLoad: { duration: 0 } }
    const colors = STATUSES.map((status) => STATUS_COLORS_RGB[status])
    const style = {
        labels: { fontFamily: "Arial", fontSize: 12, fill: labelColor },
    }
    const tooltip = (
        <VictoryTooltip
            constrainToVisibleArea={true}
            cornerRadius={4}
            flyoutPadding={5}
            flyoutStyle={{ fill: flyoutBgColor }}
            pointerWidth={20}
            renderInPortal={true}
            style={{ fontFamily: "Arial", fontSize: 12, fill: labelColor }}
        />
    )
    const dates = Object.keys(summary)
    const bbWidth = boundingBox.width ?? 0
    const bbHeight = bbWidth // Charts are round (pie chart) or square (bar chart)
    const label = (
        <VictoryPortal x={bbWidth / 2} y={bbHeight / 2}>
            <VictoryLabel
                textAnchor="middle"
                style={{ fontFamily: "Arial", fontSize: 12, fill: labelColor }}
                text={nrMetricsLabel(sum(summary[dates[0]]))}
            />
        </VictoryPortal>
    )
    const chartProps = {
        animate: animate,
        colors: colors,
        height: Math.max(bbHeight, 1), // Prevent "Failed prop type: Invalid prop range supplied to VictoryBar"
        label: label,
        maxY: maxY,
        style: style,
        tooltip: tooltip,
        width: Math.max(bbWidth, 1), // Prevent "Failed prop type: Invalid prop range supplied to VictoryBar"
    }
    return (
        <DashboardCard onClick={onClick} selected={selected} title={header}>
            <div ref={ref} aria-label={ariaChartLabel(summary)}>
                <VictoryContainer>
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
