import { useContext } from 'react';
import { VictoryAxis, VictoryChart, VictoryLabel, VictoryLine, VictoryScatter, VictoryTheme, VictoryVoronoiContainer } from 'victory';
import { DarkMode } from "../context/DarkMode";
import { DataModel } from "../context/DataModel";
import { STATUS_COLORS_RGB, capitalize, formatMetricScaleAndUnit, get_metric_name, getMetricScale, nice_number, scaled_number } from '../utils';
import { measurementsPropType, metricPropType } from '../sharedPropTypes';

function measurementAttributeAsNumber(metric, measurement, field, dataModel) {
    const scale = getMetricScale(metric, dataModel)
    const value = measurement[scale]?.[field] ?? null;
    return value !== null ? Number(value) : null;
}

export const QTStatusTooltip = (props) => {
    const { datum, x, y } = props;
    return (
        <g style={{ pointerEvents: "none" }}>
            <foreignObject
                x={x}
                y={y}
                width="250"
                height="100"
                style={{ overflow: "visible" }}
            >
                <div className="ui card" style={{ fontSize: "8px" }}>
                    <div className="ui small list">
                        <div className="item yValue" role="listitem"><StatusIcon status={datum.status} size="small" /> {datum.y} {datum.yUnits}</div>
                        <div className="item xValue" role="listitem">{datum.begin} - {datum.end}</div>
                    </div>
                </div>
            </foreignObject>
        </g >
    );
}
const ScatterPoint = ({ x, y, datum }) => {

    return <circle fill={STATUS_COLORS_RGB[datum.status]} cx={x} cy={y} r={3} />;
};

export function TrendGraph({ metric, measurements }) {
    const dataModel = useContext(DataModel)
    const darkMode = useContext(DarkMode)
    const metricName = get_metric_name(metric, dataModel);
    const unit = capitalize(formatMetricScaleAndUnit(metric, dataModel));
    const measurementValues = measurements.map((measurement) => measurementAttributeAsNumber(metric, measurement, "value", dataModel));
    let max_y = nice_number(Math.max(...measurementValues));
    let measurementPoints = [];
    let measurementLines = [];
    let measurementTooltips = []; // The measurement values as (x, y) coordinates
    let previousX2 = new Date("2000-01-01");
    measurements.forEach((measurement, index) => {
        const x1 = new Date(measurement.start);
        const x2 = new Date(measurement.end);
        // Make sure each measurement has a positive width, or VictoryChart won't draw the area
        if (x1.getTime() <= previousX2.getTime()) {
            x1.setSeconds(x1.getSeconds() + (previousX2.getSeconds() - x1.getSeconds()) + 1)
        }
        if (x2.getTime() <= x1.getTime()) {
            x2.setSeconds(x2.getSeconds() + (x1.getSeconds() - x2.getSeconds()) + 1)
        }
        previousX2 = x2
        measurementPoints.push({ y: measurementValues[index], x: x1 }, { y: measurementValues[index], x: x2 });
        let status = "unknown";
        const { percentage, count } = measurement


        console.log(metric.scale)

        switch (metric.scale) {
            case "percentage":
                status = percentage.status

                break;
            case "count":
                status = count.status
                break;
            default:
                break;

        }
        // if (percentage !== undefined) {
        //     status = percentage.status
        // }

        // if (count !== undefined) {
        //     status = count.status
        // }



        measurementTooltips.push({ y: measurementValues[index], x: new Date((x1.getTime() + x2.getTime()) / 2), status: status, begin: format(x1, "dd-MM-yyyy HH:mm"), end: format(x2, "dd-MM-yyyy HH:mm"), yUnits: unit });
    });
    const softWhite = "rgba(255, 255, 255, 0.8)"
    const softerWhite = "rgba(255, 255, 255, 0.7)"
    const axisStyle = {
        axisLabel: { padding: 30, fontSize: 11, fill: darkMode ? softWhite : null },
        tickLabels: { fontSize: 8, fill: darkMode ? softerWhite : null }
    };

    return (
        <VictoryChart
            height={250}
            scale={{ x: "time", y: "linear" }}
            style={{ parent: { height: "100%", background: darkMode ? "rgb(40, 40, 40)" : "white" } }}
            theme={VictoryTheme.material}
            containerComponent={<VictoryVoronoiContainer voronoiBlacklist={["line"]} labels={({ datum }) => `y: ${datum.y}`} mouseFollowTooltips labelComponent={<QTStatusTooltip />} />}
            width={750}
        >
            <VictoryLabel x={375} y={20} style={{ fill: darkMode ? softWhite : null }} text={metricName} textAnchor="middle" />
            <VictoryAxis
                label={"Time"}
                style={axisStyle}
            />
            <VictoryAxis
                dependentAxis
                domain={[0, max_y]}
                label={unit}
                style={axisStyle}
                tickFormat={(t) => `${scaled_number(t)}`} />
            <VictoryLine
                data={measurementPoints}
                name="line"
                interpolation="stepBefore"
                style={{ data: { stroke: darkMode ? "rgba(255, 255, 255, 0.87) " : "black", strokeWidth: 2 } }} />
            <VictoryScatter data={measurementTooltips} size={1} dataComponent={<ScatterPoint />} />

        </VictoryChart>
    )
}
TrendGraph.propTypes = {
    metric: metricPropType,
    measurements: measurementsPropType,
}
