import React from 'react';
import { VictoryBar, VictoryStack, VictoryTooltip } from 'victory';
import { pluralize, STATUSES, STATUS_COLORS, STATUS_COLORS_RGB, STATUS_NAME } from '../utils';

function nr_metrics_label(nr_metrics) {
    return nr_metrics === 0 ? "no metrics" : nr_metrics + pluralize(" metric", nr_metrics)
}

export function StatusBarChart({ summary, maxY }) {
    const style = {
        data: { stroke: 'grey', strokeWidth: 1, strokeOpacity: 0.5 },
        labels: { fontFamily: "Arial", fontSize: 36 }
    }
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
                barRatio={1}
                key={status}
                style={style}
                labels={() => null}
                labelComponent={<VictoryTooltip constrainToVisibleArea cornerRadius={6} pointerWidth={20} renderInPortal={true} />}
                data={data}
            />
        )
    });
    // Reverse the order of the bars and the colors because apparently VictoryStack reverses the order (again)
    bars.reverse();
    const colors = STATUSES.map((status) => STATUS_COLORS_RGB[status]);
    colors.reverse();
    return (
        <VictoryStack
            animate={{ duration: 0, onLoad: 0 }}
            colorScale={colors}
            domain={{ y: [0, maxY] }}
            padding={{ left: 70, right: 70, top: 0, bottom: 0 }}
        >
            {bars}
        </VictoryStack>
    )
}
