import React from 'react';
import { VictoryGroup, VictoryLine, VictoryTheme } from 'victory';

export function TrendSparkline(props) {
  let measurements = [];
  for (var i = 0; i < props.measurements.length; i++) {
    const measurement = props.measurements[i];
    const value = measurement[props.scale].value || null;
    const y = value !== null ? Number(value) : null;
    const x1 = new Date(measurement.start);
    const x2 = new Date(measurement.end);
    measurements.push({y: y, x: x1});
    measurements.push({y: y, x: x2});
  }
  return (
    <VictoryGroup theme={VictoryTheme.material} scale={{ x: "time", y: "linear" }} height={60} padding={0}>
      <VictoryLine data={measurements} interpolation="stepBefore" style={{
        data: {
          stroke: "black", strokeWidth: 3
        }
      }}/>
    </VictoryGroup>
  )
}
