import { oneOf } from "prop-types"
import { useContext } from "react"
import { Placeholder, PlaceholderImage } from "semantic-ui-react"
import { VictoryAxis, VictoryChart, VictoryLabel, VictoryLine, VictoryTheme } from "victory"

import { DarkMode } from "../context/DarkMode"
import { DataModel } from "../context/DataModel"
import { measurementsPropType, metricPropType } from "../sharedPropTypes"
import { capitalize, formatMetricScaleAndUnit, getMetricName, getMetricScale, niceNumber, scaledNumber } from "../utils"
import { WarningMessage } from "../widgets/WarningMessage"

function measurementAttributeAsNumber(metric, measurement, field, dataModel) {
    const scale = getMetricScale(metric, dataModel)
    const value = measurement[scale]?.[field] ?? null
    return value !== null ? Number(value) : null
}

export function TrendGraph({ metric, measurements, loading }) {
    const dataModel = useContext(DataModel)
    const darkMode = useContext(DarkMode)
    const chartHeight = 250
    const estimatedTotalChartHeight = chartHeight + 200 // Estimate of the height including title and axis
    if (getMetricScale(metric, dataModel) === "version_number") {
        return (
            <WarningMessage
                content="Trend graphs are not supported for metrics with a version number scale."
                header="Trend graph not supported for version numbers"
            />
        )
    }
    if (loading === "failed") {
        return (
            <WarningMessage
                content="Loading the measurements from the API-server failed."
                header="Loading measurements failed"
            />
        )
    }
    if (loading === "loading") {
        return (
            <Placeholder fluid inverted={darkMode} style={{ height: estimatedTotalChartHeight }}>
                <PlaceholderImage />
            </Placeholder>
        )
    }
    if (measurements.length === 0) {
        return (
            <WarningMessage
                content="A trend graph can not be displayed until this metric has measurements."
                header="No measurements"
            />
        )
    }
    const metricName = getMetricName(metric, dataModel)
    const unit = capitalize(formatMetricScaleAndUnit(metric, dataModel))
    const measurementValues = measurements.map((measurement) =>
        measurementAttributeAsNumber(metric, measurement, "value", dataModel),
    )
    let max_y = niceNumber(Math.max(...measurementValues))
    let measurementPoints = [] // The measurement values as (x, y) coordinates
    let previousX2 = new Date("2000-01-01")
    measurements.forEach((measurement, index) => {
        const x1 = new Date(measurement.start)
        const x2 = new Date(measurement.end)
        // Make sure each measurement has a positive width, or VictoryChart won't draw the area
        if (x1.getTime() <= previousX2.getTime()) {
            x1.setSeconds(x1.getSeconds() + (previousX2.getSeconds() - x1.getSeconds()) + 1)
        }
        if (x2.getTime() <= x1.getTime()) {
            x2.setSeconds(x2.getSeconds() + (x1.getSeconds() - x2.getSeconds()) + 1)
        }
        previousX2 = x2
        measurementPoints.push({ y: measurementValues[index], x: x1 }, { y: measurementValues[index], x: x2 })
    })
    const softWhite = "rgba(255, 255, 255, 0.8)"
    const softerWhite = "rgba(255, 255, 255, 0.7)"
    const axisStyle = {
        axisLabel: { padding: 30, fontSize: 11, fill: darkMode ? softWhite : null },
        tickLabels: { fontSize: 8, fill: darkMode ? softerWhite : null },
    }
    return (
        <VictoryChart
            height={chartHeight}
            scale={{ x: "time", y: "linear" }}
            style={{
                parent: { height: "100%", background: darkMode ? "rgb(40, 40, 40)" : "white" },
            }}
            theme={VictoryTheme.material}
            width={750}
        >
            <VictoryLabel
                x={375}
                y={20}
                style={{ fill: darkMode ? softWhite : null }}
                text={metricName}
                textAnchor="middle"
            />
            <VictoryAxis label={"Time"} style={axisStyle} />
            <VictoryAxis
                dependentAxis
                domain={[0, max_y]}
                label={unit}
                style={axisStyle}
                tickFormat={(t) => `${scaledNumber(t)}`}
            />
            <VictoryLine
                data={measurementPoints}
                interpolation="stepBefore"
                style={{
                    data: {
                        stroke: darkMode ? "rgba(255, 255, 255, 0.87) " : "black",
                        strokeWidth: 2,
                    },
                }}
            />
        </VictoryChart>
    )
}
TrendGraph.propTypes = {
    loading: oneOf(["failed", "loaded", "loading"]),
    metric: metricPropType,
    measurements: measurementsPropType,
}
