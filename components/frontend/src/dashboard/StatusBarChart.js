import React from 'react';
import { VictoryBar, VictoryStack } from 'victory';
import { pluralize, STATUSES, STATUS_COLORS, STATUS_NAME, sum } from '../utils';

function nrMetricsLabel(nrMetrics) {
    return nrMetrics === 0 ? "No metrics" : nrMetrics + pluralize(" metric", nrMetrics)
}

export function StatusBarChart({ animate, colors, label, tooltip, summary, maxY, style, width, height }) {
    const nrMetrics = sum(summary[Object.keys(summary)[0]])
    const nrDates = Object.keys(summary).length
    // Calculate how many metrics this chart displays compared to the chart with the most metrics.
    // The ratio is used below to set the bar width so that bars in charts that represent fewer
    // metrics are smaller than bars in charts that represent more metrics. The calculatation is not
    // simply `nrMetrics / maxY` because that makes the bars in charts that represent just a few metrics
    // too small to see. By adding maxY to both the numerator and the denominator the smallest bars are
    // at least half as wide as the maximum width.
    const barRatio = maxY > 0 ? (nrMetrics + maxY) / (2 * maxY) : 1
    // Create a VictoryBar for each status
    const bars = STATUSES.map((status) => {
        const data = [];
        Object.entries(summary).forEach(([date, count]) => {
            const dateString = new Date(date).toLocaleDateString();
            const y = count[STATUS_COLORS[status]];
            data.push({ x: date, y: y, label: `${dateString}\n${STATUS_NAME[status]}: ${nrMetricsLabel(y)}` })
        })
        return (
            <VictoryBar
                barRatio={barRatio}
                key={status}
                style={style}
                labels={() => null}
                labelComponent={tooltip}
                data={data}
                animate={animate}
            />
        )
    });
    // Reverse the order of the bars and the colors because apparently VictoryStack reverses the order (again)
    bars.reverse();
    colors.reverse();
    // Because the bars are wider if the chart is wider, horizontal padding needs to be relative to chart width
    const horizontalPadding = width / 8
    const verticalPadding = 10
    return (
        nrMetrics === 0 ? label :
            <VictoryStack
                colorScale={colors}
                key={nrDates}  // Make sure the stack is redrawn when the users changes the number of dates to display
                padding={{ left: horizontalPadding, right: horizontalPadding, top: verticalPadding, bottom: verticalPadding }}
                width={width}
                height={height}
                standalone={false}
            >
                {bars}
            </VictoryStack>
    )
}
