import React from 'react';
import { VictoryPie } from 'victory';

export function StatusPieChart(props) {
    const nr_metrics = props.red + props.green + props.yellow + props.grey + props.white;
    const radius = 175;
    const innerRadius = Math.max(0, (radius - 50) - Math.pow(nr_metrics, 1.35));
    return (
        <VictoryPie
            colorScale={["rgb(211,59,55)", "rgb(30,148,78)", "rgb(253,197,54)", "rgb(150,150,150)", "rgb(245,245,245)"]}
            padding={20}
            style={{
                data: { stroke: 'grey', strokeWidth: 1, strokeOpacity: 0.5 }
            }}
            radius={radius}
            innerRadius={innerRadius}
            labels={() => null}
            animate={{ duration: 2000 }}
            data={[
                { y: props.red },
                { y: props.green },
                { y: props.yellow },
                { y: props.grey },
                { y: props.white }
            ]}
        />
    )
}
