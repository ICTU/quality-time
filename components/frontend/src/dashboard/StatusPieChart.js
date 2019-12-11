import React from 'react';
import { VictoryLabel, VictoryPie, VictoryTooltip } from 'victory';

function nr_metrics_text(nr_metrics) {
    return [nr_metrics === 0 ? "No" : nr_metrics, "metric" + (nr_metrics === 1 ? "" : "s")]
}

function nr_metrics_label(nr_metrics) {
    return nr_metrics === 0 ? "no" : nr_metrics + " metric" + (nr_metrics === 1 ? "" : "s")
}

export function StatusPieChart(props) {
    const nr_metrics = props.red + props.green + props.yellow + props.grey + props.white;
    const radius = 175;
    const innerRadius = Math.max(60, (radius - 50) - Math.pow(nr_metrics, 1.35));
    return (
        <svg viewBox="0 0 400 400">
            <VictoryLabel
                textAnchor="middle"
                style={{ fill: "grey", fontFamily: "Arial", fontSize: 30 }}
                x={200} y={200}
                text={nr_metrics_text(nr_metrics)}
            />
            {nr_metrics > 0 &&
                <VictoryPie
                    colorScale={["rgb(211,59,55)", "rgb(30,148,78)", "rgb(253,197,54)", "rgb(150,150,150)", "rgb(245,245,245)"]}
                    padding={20}
                    style={{
                        data: { stroke: 'grey', strokeWidth: 1, strokeOpacity: 0.5 },
                        labels: { fontFamily: "Arial", fontSize: 36 }
                    }}
                    radius={radius}
                    innerRadius={innerRadius}
                    standalone={false}
                    width={400} height={400}
                    labels={() => null}
                    labelComponent={<VictoryTooltip constrainToVisibleArea cornerRadius={6} renderInPortal={false} />}
                    animate={{ duration: 2000 }}
                    data={[
                        { y: props.red, label: `Target not met: ${nr_metrics_label(props.red)}` },
                        { y: props.green, label: `Target met: ${nr_metrics_label(props.green)}` },
                        { y: props.yellow, label: `Near target: ${nr_metrics_label(props.yellow)}` },
                        { y: props.grey, label: `Technical debt target met: ${nr_metrics_label(props.grey)}` },
                        { y: props.white, label: `Unknown: ${nr_metrics_label(props.white)}` }
                    ]}
                />
            }
        </svg>
    )
}
