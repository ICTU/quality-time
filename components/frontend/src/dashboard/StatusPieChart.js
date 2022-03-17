import React, { useContext } from 'react';
import { VictoryLabel, VictoryPie, VictoryTooltip } from 'victory';
import { DarkMode } from '../context/DarkMode';
import { pluralize } from '../utils';

function nr_metrics_text(nr_metrics) {
    return [nr_metrics === 0 ? "No" : nr_metrics, pluralize("metric", nr_metrics)]
}

function nr_metrics_label(nr_metrics) {
    return nr_metrics === 0 ? "no metrics" : nr_metrics + pluralize(" metric", nr_metrics)
}

export function StatusPieChart({ green, red, yellow, grey, white }) {
    function pie_chart_label() {
        let label = 'Status pie chart: ' + nr_metrics_label(nr_metrics);
        if (green > 0) { label += `, ${green} target met` }
        if (red > 0) { label += `, ${red} target not met` }
        if (yellow > 0) { label += `, ${yellow} near target` }
        if (grey > 0) { label += `, ${grey} with accepted technical debt` }
        if (white > 0) { label += `, ${white} with unknown status` }
        return label
    }
    const nr_metrics = red + green + yellow + grey + white;
    const radius = 175;
    const innerRadius = Math.max(60, (radius - 50) - Math.pow(nr_metrics, 1.35));
    const labelColor = useContext(DarkMode) ? "lightgrey" : "darkgrey";
    return (
        <svg viewBox="0 0 400 400" aria-label={pie_chart_label()}>
            <VictoryLabel
                textAnchor="middle"
                style={{ fill: labelColor, fontFamily: "Arial", fontSize: 30 }}
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
                        { y: red, label: `Target not met: ${nr_metrics_label(red)}` },
                        { y: green, label: `Target met: ${nr_metrics_label(green)}` },
                        { y: yellow, label: `Near target: ${nr_metrics_label(yellow)}` },
                        { y: grey, label: `Technical debt target met: ${nr_metrics_label(grey)}` },
                        { y: white, label: `Unknown: ${nr_metrics_label(white)}` }
                    ]}
                />
            }
        </svg>
    )
}
