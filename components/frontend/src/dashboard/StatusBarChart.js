import React from 'react';
import { VictoryBar, VictoryContainer, VictoryStack } from 'victory';
import { pluralize, STATUSES, STATUS_COLORS, STATUS_NAME, sum } from '../utils';

function nr_metrics_label(nr_metrics) {
    return nr_metrics === 0 ? "no metrics" : nr_metrics + pluralize(" metric", nr_metrics)
}

export function StatusBarChart({ animate, colors, label, tooltip, summary, maxY, style }) {
    const nrMetrics = sum(summary[Object.keys(summary)[0]])
    const barRatio = Math.max(5, nrMetrics) / maxY
    // Create a VictoryBar for each status
    const bars = STATUSES.map((status) => {
        const data = [];
        Object.entries(summary).forEach(([date, count]) => {
            const dateString = new Date(date).toLocaleDateString();
            const y = count[STATUS_COLORS[status]];
            data.push({ x: date, y: y, label: `${dateString}\n${STATUS_NAME[status]}: ${nr_metrics_label(y)}` })
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
    return (
        <svg viewBox="0 0 400 400">
            {nrMetrics === 0 && label}
            <VictoryStack
                colorScale={colors}
                containerComponent={<VictoryContainer responsive={false} />}
                domainPadding={10}
                padding={{ left: 0, right: 0, top: 10, bottom: 10 }}
                standalone={false}
                width={400} height={400}
            >
                {bars}
            </VictoryStack>
        </svg>
    )
}
