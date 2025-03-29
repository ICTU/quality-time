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
    let maxY = niceNumber(Math.max(...measurementValues))
    let measurementPoints = [] // The measurement values as (x, y) coordinates
    measurements.forEach((measurement, index) => {
        measurementPoints.push(
            { y: measurementValues[index], x: new Date(measurement.start) },
            { y: measurementValues[index], x: new Date(measurement.end) },
        )
    })
    const axisStyle = {
        axisLabel: { padding: 30, fontSize: 11, fill: color, fontFamily: fontFamily },
        tickLabels: { fontSize: 8, fill: color, fontFamily: fontFamily },
    }
    return (
        <VictoryChart
            aria-label={`Trend graph for the metric ${metricName}`}
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
                domain={[0, maxY]}
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
