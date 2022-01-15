import React from 'react';
import { VictoryGroup, VictoryLine, VictoryTheme } from 'victory';

export function TrendSparkline({ measurements, scale, report_date }) {
    if (scale === "version_number") { return null }
    let points = [];
    for (let measurement of measurements) {
        const value = (measurement[scale] && measurement[scale].value) || null;
        const y = value !== null ? Number(value) : null;
        const x1 = new Date(measurement.start);
        const x2 = new Date(measurement.end);
        points.push({ y: y, x: x1 });
        points.push({ y: y, x: x2 });
    }
    const now = report_date ? new Date(report_date) : new Date();
    let week_ago = report_date ? new Date(report_date) : new Date();
    week_ago.setDate(week_ago.getDate() - 7);
    // The width property below is not used according to https://formidable.com/open-source/victory/docs/common-props#width,
    // but setting it prevents these messages in the console: "Warning: `Infinity` is an invalid value for the `width` css style property.""
    return (
        <VictoryGroup theme={VictoryTheme.material} scale={{ x: "time", y: "linear" }} domain={{ x: [week_ago, now] }} height={30} padding={0}>
            <VictoryLine data={points} interpolation="stepBefore" style={{
                data: {
                    stroke: "black", strokeWidth: 3, width: "100%"
                }
            }} />
        </VictoryGroup>
    )
}
