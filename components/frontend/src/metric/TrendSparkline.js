import React from 'react';
import { VictoryGroup, VictoryLine, VictoryTheme } from 'victory';

export function TrendSparkline(props) {
    let measurements = [];
    for (let measurement of props.measurements) {
        const value = (measurement[props.scale] && measurement[props.scale].value) || null;
        const y = value !== null ? Number(value) : null;
        const x1 = new Date(measurement.start);
        const x2 = new Date(measurement.end);
        measurements.push({ y: y, x: x1 });
        measurements.push({ y: y, x: x2 });
    }
    const now = props.report_date ? new Date(props.report_date) : new Date();
    let week_ago = props.report_date ? new Date(props.report_date) : new Date();
    week_ago.setDate(week_ago.getDate() - 7);
    // The width property below is not used according to https://formidable.com/open-source/victory/docs/common-props#width,
    // but setting it prevents these messages in the console: "Warning: `Infinity` is an invalid value for the `width` css style property.""
    return (
        <VictoryGroup theme={VictoryTheme.material} scale={{ x: "time", y: "linear" }} domain={{ x: [week_ago, now] }} height={30} padding={0}>
            <VictoryLine data={measurements} interpolation="stepBefore" style={{
                data: {
                    stroke: "black", strokeWidth: 3, width: "100%"
                }
            }} />
        </VictoryGroup>
    )
}
