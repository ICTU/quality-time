import { useTheme } from "@mui/material"
import { useContext, useState } from "react"
import {
    createContainer,
    Point,
    VictoryAxis,
    VictoryBrushContainer,
    VictoryChart,
    VictoryLabel,
    VictoryLine,
    VictoryScatter,
    VictoryTheme,
    VictoryTooltip,
} from "victory"

import { DataModel } from "../context/DataModel"
import { loadingPropType, measurementsPropType, metricPropType } from "../sharedPropTypes"
import { capitalize, formatMetricScaleAndUnit, getMetricName, getMetricScale, scaledNumber } from "../utils"
import { LoadingPlaceHolder } from "../widgets/Placeholder"
import { FailedToLoadMeasurementsWarningMessage, InfoMessage, WarningMessage } from "../widgets/WarningMessage"
import { STATUS_COLORS, STATUS_NAME } from "./status"

function measurementAttributeAsNumber(metric, measurement, field, dataModel) {
    const scale = getMetricScale(metric, dataModel)
    const value = measurement[scale]?.[field] ?? null
    return value !== null ? Number(value) : null
}

export function TrendGraph({ metric, measurements, loading }) {
    const dataModel = useContext(DataModel)
    const [visibleDomain, setVisibleDomain] = useState({})
    const primaryColor = useTheme().palette.text.primary
    const secondaryColor = useTheme().palette.text.secondary
    const bgcolor = useTheme().palette.background.secondary
    const fontFamily = useTheme().typography.fontFamily
    const chartHeight = 250
    const chartWidth = 750
    const estimatedTotalChartHeight = chartHeight + 200 // Estimate of the height including title and axis
    if (getMetricScale(metric, dataModel) === "version_number") {
        return (
            <InfoMessage title="Trend graph not supported for version numbers">
                Trend graphs are not supported for metrics with a version number scale.
            </InfoMessage>
        )
    }
    if (loading === "failed") {
        return <FailedToLoadMeasurementsWarningMessage />
    }
    if (loading === "loading") {
        return <LoadingPlaceHolder height={estimatedTotalChartHeight} />
    }
    if (measurements.length === 0) {
        return (
            <WarningMessage title="No measurements">
                A trend graph can not be displayed until this metric has measurements.
            </WarningMessage>
        )
    }
    const metricName = getMetricName(metric, dataModel)
    const scale = getMetricScale(metric, dataModel)
    const unit = capitalize(formatMetricScaleAndUnit(metric, dataModel))
    const measurementValues = measurements.map((measurement) =>
        measurementAttributeAsNumber(metric, measurement, "value", dataModel),
    )
    let maxY = Math.max(...measurementValues)
    let measurementPoints = [] // The measurement values as (x, y) coordinates
    measurements.forEach((measurement, index) => {
        const status = measurement[scale]?.status ?? "unknown"
        measurementPoints.push({ y: measurementValues[index], x: new Date(measurement.start), status: status })
        if (measurement.start !== measurement.end) {
            measurementPoints.push({ y: measurementValues[index], x: new Date(measurement.end), status: status })
        }
    })
    const axisStyle = {
        axisLabel: { padding: 30, fontSize: 11, fill: secondaryColor, fontFamily: fontFamily },
        tickLabels: { fontSize: 8, fill: secondaryColor, fontFamily: fontFamily },
    }
    const toolTipStyle = { fill: bgcolor, fontSize: 7, fontFamily: fontFamily }
    const VictoryZoomVoronoiContainer = createContainer("zoom", "voronoi")
    return (
        <div>
            <VictoryChart
                aria-label={`Trend graph for the metric ${metricName}`}
                containerComponent={
                    <VictoryZoomVoronoiContainer
                        allowZoom={false} // Disable zoom via scrolling
                        responsive={true}
                        zoomDimension="x"
                        zoomDomain={visibleDomain}
                        onZoomDomainChange={setVisibleDomain}
                        events={{
                            onWheelCapture: (event) => event.stopPropagation(), // Needed to make normal scroll work
                        }}
                    />
                }
                height={chartHeight}
                padding={{
                    top: 50,
                    left: 50,
                    right: 30,
                    bottom: 30,
                }}
                scale={{ x: "time", y: "linear" }}
                style={{ parent: { height: "100%", background: bgcolor }, fontFamily: fontFamily }}
                theme={VictoryTheme.material}
                width={chartWidth}
            >
                <VictoryLabel
                    x={375}
                    y={20}
                    style={{ fill: secondaryColor, fontFamily: fontFamily }}
                    text={metricName}
                    textAnchor="middle"
                />
                <VictoryAxis style={axisStyle} />
                <VictoryAxis
                    dependentAxis
                    domain={[0, maxY]}
                    label={unit}
                    style={axisStyle}
                    tickFormat={(t) => `${scaledNumber(t)}`}
                />
                <VictoryLine
                    data={measurementPoints}
                    interpolation="stepBefore"
                    style={{
                        data: { stroke: secondaryColor, strokeWidth: 1 },
                    }}
                />
                <VictoryScatter
                    data={measurementPoints}
                    dataComponent={<Point data-testid="Point" />}
                    style={{
                        data: {
                            fill: ({ datum }) => STATUS_COLORS[datum.status],
                            stroke: secondaryColor,
                            strokeWidth: 1,
                        },
                    }}
                    labelComponent={<VictoryTooltip style={toolTipStyle} />}
                    labels={({ datum }) => {
                        const date = datum.x.toLocaleString([], { dateStyle: "short", timeStyle: "short" })
                        const status = STATUS_NAME[datum.status].toLowerCase()
                        return `${datum.y} ${unit} (${status}) on ${date}`
                    }}
                />
            </VictoryChart>
            <VictoryChart
                aria-label={`Brush graph for the metric ${metricName}`}
                containerComponent={
                    <VictoryBrushContainer
                        brushDimension="x"
                        brushDomain={visibleDomain}
                        brushStyle={{ fill: primaryColor, fillOpacity: 0.2 }}
                        defaultBrushArea="move" // Move the brush area when the user clicks outside the brush area
                        onBrushDomainChange={setVisibleDomain}
                    />
                }
                height={50}
                padding={{
                    top: 0,
                    left: 50,
                    right: 30,
                    bottom: 30,
                }}
                scale={{ x: "time", y: "linear" }}
                style={{ parent: { height: "100%", background: bgcolor }, fontFamily: fontFamily }}
                theme={VictoryTheme.material}
                width={chartWidth}
            >
                <VictoryAxis label={"Time"} style={axisStyle} />
                <VictoryLine
                    data={measurementPoints}
                    interpolation="stepBefore"
                    style={{ data: { stroke: secondaryColor, strokeWidth: 1 } }}
                />
            </VictoryChart>
        </div>
    )
}
TrendGraph.propTypes = {
    loading: loadingPropType,
    metric: metricPropType,
    measurements: measurementsPropType,
}
