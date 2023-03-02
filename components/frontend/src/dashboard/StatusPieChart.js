import React from 'react';
import { VictoryPie } from 'victory';
import { pluralize, STATUSES, STATUS_COLORS, STATUS_NAME, sum } from '../utils';

function nr_metrics_label(nr_metrics) {
    return nr_metrics === 0 ? "no metrics" : nr_metrics + pluralize(" metric", nr_metrics)
}

export function StatusPieChart({ animate, colors, label, tooltip, summary, style }) {
    function pie_chart_label() {
        let label = 'Status pie chart: ' + nr_metrics_label(nr_metrics);
        if (summary.green > 0) { label += `, ${summary.green} target met` }
        if (summary.red > 0) { label += `, ${summary.red} target not met` }
        if (summary.yellow > 0) { label += `, ${summary.yellow} near target` }
        if (summary.grey > 0) { label += `, ${summary.grey} with accepted technical debt` }
        if (summary.blue > 0) { label += `, ${summary.blue} informative` }
        if (summary.white > 0) { label += `, ${summary.white} with unknown status` }
        return label
    }
    const nr_metrics = sum(summary)
    const radius = 175;
    const innerRadius = Math.max(60, (radius - 50) - Math.pow(nr_metrics, 1.35));
    const data = STATUSES.map((status) => {
        const y = summary[STATUS_COLORS[status]]
        return { y: y, label: `${STATUS_NAME[status]}: ${nr_metrics_label(y)}` }
    })
    return (
        <svg viewBox="0 0 400 400" aria-label={pie_chart_label()}>
            {label}
            {nr_metrics > 0 &&
                <VictoryPie
                    animate={animate}
                    colorScale={colors}
                    padding={20}
                    radius={radius}
                    innerRadius={innerRadius}
                    standalone={false}
                    style={style}
                    width={400} height={400}
                    labels={() => null}
                    labelComponent={tooltip}
                    data={data}
                />
            }
        </svg>
    )
}
