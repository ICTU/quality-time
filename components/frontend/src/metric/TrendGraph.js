import { useTheme } from "@mui/material"
import { useContext } from "react"
import { VictoryAxis, VictoryChart, VictoryLabel, VictoryLine, VictoryTheme } from "victory"

import { DataModel } from "../context/DataModel"
import { loadingPropType, measurementsPropType, metricPropType } from "../sharedPropTypes"
import { capitalize, formatMetricScaleAndUnit, getMetricName, getMetricScale, niceNumber, scaledNumber } from "../utils"
import { LoadingPlaceHolder } from "../widgets/Placeholder"
import { FailedToLoadMeasurementsWarningMessage, InfoMessage, WarningMessage } from "../widgets/WarningMessage"

function measurementAttributeAsNumber(metric, measurement, field, dataModel) {
    const scale = getMetricScale(metric, dataModel)
    const value = measurement[scale]?.[field] ?? null
    return value !== null ? Number(value) : null
}

export function TrendGraph({ metric, measurements, loading }) {
    const dataModel = useContext(DataModel)
    const color = useTheme().palette.text.secondary
    const bgcolor = useTheme().palette.background.secondary
    const fontFamily = useTheme().typography.fontFamily
    const chartHeight = 250
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
    const axisStyle = {
        axisLabel: { padding: 30, fontSize: 11, fill: color, fontFamily: fontFamily },
        tickLabels: { fontSize: 8, fill: color, fontFamily: fontFamily },
    }
    return (
        <VictoryChart
            height={chartHeight}
            scale={{ x: "time", y: "linear" }}
            style={{ parent: { height: "100%", background: bgcolor }, fontFamily: fontFamily }}
            theme={VictoryTheme.material}
            width={750}
        >
            <VictoryLabel
                x={375}
                y={20}
                style={{ fill: color, fontFamily: fontFamily }}
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
                style={{ data: { stroke: color, strokeWidth: 2 } }}
            />
        </VictoryChart>
    )
}
TrendGraph.propTypes = {
    loading: loadingPropType,
    metric: metricPropType,
    measurements: measurementsPropType,
}
