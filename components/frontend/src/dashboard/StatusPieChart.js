import React from 'react';
import { VictoryLabel, VictoryPie } from 'victory';

export function StatusPieChart(props) {
    const nr_metrics = props.red + props.green + props.yellow + props.grey + props.white;
    const radius = 175;
    const innerRadius = Math.max(60, (radius - 50) - Math.pow(nr_metrics, 1.35));
    return (
        <svg viewBox="0 0 400 400">
            {nr_metrics > 0 &&
                <VictoryPie
                    colorScale={["rgb(211,59,55)", "rgb(30,148,78)", "rgb(253,197,54)", "rgb(150,150,150)", "rgb(245,245,245)"]}
                    padding={20}
                    style={{
                        data: { stroke: 'grey', strokeWidth: 1, strokeOpacity: 0.5 }
                    }}
                    radius={radius}
                    innerRadius={innerRadius}
                    standalone={false}
                    width={400} height={400}
                    labels={() => null}
                    animate={{ duration: 2000 }}
                    data={[
                        { y: props.red },
                        { y: props.green },
                        { y: props.yellow },
                        { y: props.grey },
                        { y: props.white }
                    ]}
                />}
            <VictoryLabel
                textAnchor="middle"
                style={{ fill: "grey", fontFamily: "Arial", fontSize: 30 }}
                x={200} y={200}
                text={[nr_metrics === 0 ? "No" : nr_metrics, "metric" + (nr_metrics === 1 ? "" : "s")]}
            />
        </svg>
    )
}
