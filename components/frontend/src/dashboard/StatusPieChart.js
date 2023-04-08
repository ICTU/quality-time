import React from 'react';
import { VictoryPie } from 'victory';
import { pluralize, STATUSES, STATUS_COLORS, STATUS_NAME, sum } from '../utils';

function nrMetricsLabel(nrMetrics) {
    return nrMetrics === 0 ? "No metrics" : nrMetrics + pluralize(" metric", nrMetrics)
}

export function StatusPieChart({ animate, colors, label, tooltip, summary, style, maxY, width, height }) {
    const nrMetrics = sum(summary)
    const outerRadius = 0.4 * Math.min(height, width);
    const minInnerRadius = 0.4 * outerRadius
    const maxInnerRadius = 0.7 * outerRadius
    const innerRadius = maxInnerRadius - (maxInnerRadius - minInnerRadius) * (nrMetrics / maxY)
    const data = STATUSES.map((status) => {
        const y = summary[STATUS_COLORS[status]]
        return { y: y, label: `${STATUS_NAME[status]}: ${nrMetricsLabel(y)}` }
    })
    return (
        <>
            {label}
            {nrMetrics > 0 &&
                <VictoryPie
                    animate={animate}
                    colorScale={colors}
                    radius={outerRadius}
                    innerRadius={innerRadius}
                    standalone={false}
                    style={style}
                    labels={() => null}
                    labelComponent={tooltip}
                    data={data}
                    width={width}
                    height={height}
                />
            }
        </>
    )
}
