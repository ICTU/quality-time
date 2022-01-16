import React from 'react';
import { VictoryGroup, VictoryLine, VictoryTheme } from 'victory';
import { pluralize } from '../utils';

export function TrendSparkline({ measurements, scale, report_date }) {
    if (scale === "version_number") { return null }
    let points = [];
    let yvalues = new Set();
    for (let measurement of measurements) {
        const value = (measurement[scale] && measurement[scale].value) || null;
        const y = value !== null ? Number(value) : null;
        if (y !== null) { yvalues.add(y) }
        const x1 = new Date(measurement.start);
        const x2 = new Date(measurement.end);
        points.push({ y: y, x: x1 });
        points.push({ y: y, x: x2 });
    }
    const now = report_date ? new Date(report_date) : new Date();
    let week_ago = report_date ? new Date(report_date) : new Date();
    week_ago.setDate(week_ago.getDate() - 7);
    const ariaLabel = `sparkline graph showing ${yvalues.size} different measurement ${pluralize("value", yvalues.size)} in the week before ${report_date ? now.toLocaleDateString() : "today"}`
    // The width property below is not used according to https://formidable.com/open-source/victory/docs/common-props#width,
    // but setting it prevents these messages in the console: "Warning: `Infinity` is an invalid value for the `width` css style property.""
    return (
        <div aria-label={ariaLabel}>
            <VictoryGroup theme={VictoryTheme.material} scale={{ x: "time", y: "linear" }} domain={{ x: [week_ago, now] }} height={30} padding={0}>
                <VictoryLine data={points} interpolation="stepBefore" style={{
                    data: {
                        stroke: "black", strokeWidth: 3, width: "100%"
                    }
                }} />
            </VictoryGroup>
        </div>
    )
}
