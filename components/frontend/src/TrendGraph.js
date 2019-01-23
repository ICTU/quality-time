import React from 'react';
import { VictoryChart, VictoryLine, VictoryTheme, VictoryAxis } from 'victory';

function readableNumber(number) {
  var scale = ['', 'k', 'm'];
  var exponent = Math.floor(Math.log(number) / Math.log(1000));
  return (number / Math.pow(1000, exponent)).toFixed(0) + scale[exponent];
}

function TrendGraph(props) {
  let measurements = [];
  let targets = [];
  let max_y = 100;
  for (var i = 0; i < props.measurements.length; i++) {
    const measurement = props.measurements[i].measurement;
    const m = measurement.measurement !== null ? Number(measurement.measurement) : null;
    if (m !== null && m > max_y) {max_y = m}
    const t = Number(measurement.target);
    if (t > max_y) {max_y = t}
    const x1 = new Date(measurement.start);
    const x2 = new Date(measurement.end);
    measurements.push({y: m, x: x1});
    measurements.push({y: m, x: x2});
    targets.push({y: t, x: x1});
    targets.push({y: t, x: x2});
  }
  return (
    <VictoryChart theme={VictoryTheme.material} style={{parent: {background: "white"}}} scale={{ x: "time", y: "linear" }}>
      <VictoryAxis/>
      <VictoryAxis dependentAxis label={props.unit} style={{axisLabel: {padding: 35 }}} domain={[0, max_y]}
        tickFormat={(t) => `${readableNumber(t)}`} />
      <VictoryLine data={measurements} interpolation="stepBefore" style={{
        data: {
          stroke: "black", strokeWidth: 1
        }
      }}/>
      <VictoryLine data={targets} style={{
        data: {
          stroke: "green", strokeWidth: 1, strokeDasharray: "3 3"
        }
      }}/>
    </VictoryChart>
  )
}


export { TrendGraph };
