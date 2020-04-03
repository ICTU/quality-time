import React from 'react';
import { VictoryAxis, VictoryChart, VictoryLabel, VictoryLine, VictoryTheme, VictoryArea, VictoryStack } from 'victory';

function readableNumber(number) {
  var scale = ['', 'k', 'm'];
  var exponent = Math.floor(Math.log(number) / Math.log(1000));
  return (number / Math.pow(1000, exponent)).toFixed(0) + scale[exponent];
}

function Background({ data, ...props }) {
  return (
    <VictoryStack {...props} >
      <VictoryArea
        data={data.green}
        interpolation="stepBefore"
        style={{ data: { fill: "rgb(30,148,78,0.7)", opacity: 0.7, stroke: "rgb(30,148,78)", strokeWidth: 0 } }} />
      <VictoryArea
        data={data.grey}
        interpolation="stepBefore"
        style={{ data: { fill: "rgb(150,150,150,0.7)", opacity: 0.7, stroke: "rgb(150,150,150)", strokeWidth: 0 } }} />
      <VictoryArea
        data={data.yellow}
        interpolation="stepBefore"
        style={{ data: { fill: "rgb(253,197,54,0.7)", opacity: 0.7, stroke: "rgb(253,197,54)", strokeWidth: 0 } }} />
      <VictoryArea
        data={data.red}
        interpolation="stepBefore"
        style={{ data: { fill: "rgb(211,59,55,0.7)", opacity: 0.7, stroke: "rgb(253,197,54)", strokeWidth: 0 } }} />
    </VictoryStack>
  )
}

export function TrendGraph(props) {
  let measurement_values = [];
  let target_values = [];
  let near_target_values = [];
  let debt_target_values = [];

  for (var i = 0; i < props.measurements.length; i++) {
    const measurement = props.measurements[i];
    const value = (measurement[props.scale] && measurement[props.scale].value) || null;
    measurement_values.push(value !== null ? Number(value) : null);
    const target = (measurement[props.scale] && measurement[props.scale].target) || null;
    target_values.push(target !== null ? Number(target) : null);
    const near_target = (measurement[props.scale] && measurement[props.scale].near_target) || null;
    near_target_values.push(near_target !== null ? Number(near_target) : null);
    const debt_target = (measurement[props.scale] && measurement[props.scale].debt_target) || null;
    debt_target_values.push(debt_target !== null ? Number(debt_target) : null);
  }
  let max_y = Math.max(
    Math.max(...measurement_values), Math.max(...target_values),
    Math.max(...near_target_values), Math.max(...debt_target_values));
  if (max_y < 18) { max_y = 20 } else if (max_y < 45) { max_y = 50 } else if (max_y < 90) { max_y = 100 } else { max_y += 20 }

  let measurements = [];
  let green = [];
  let grey = [];
  let yellow = [];
  let red = [];
  for (i = 0; i < props.measurements.length; i++) {
    const measurement = props.measurements[i];
    const x1 = new Date(measurement.start);
    const x2 = new Date(measurement.end);
    measurements.push({ y: measurement_values[i], x: x1 }, { y: measurement_values[i], x: x2 });
    const green_y = target_values[i];
    if (green_y !== null) {
      green.push({ y: green_y, x: x1 });
      const grey_y = debt_target_values[i] !== null ? Math.max(0, debt_target_values[i] - green_y) : 0;
      grey.push({ y: grey_y, x: x1 });
      const yellow_y = Math.max(0, near_target_values[i] - (grey_y + green_y));
      yellow.push({ y: yellow_y, x: x1 });
      const red_y = max_y - (yellow_y + grey_y + green_y);
      red.push({ y: red_y, x: x1 });
      if (x1.getTime() !== x2.getTime()) {
        green.push({ y: green_y, x: x2 });
        grey.push({ y: grey_y, x: x2 });
        yellow.push({ y: yellow_y, x: x2 });
        red.push({ y: red_y, x: x2 });
      }
    }
  }
  const axisStyle = { axisLabel: { padding: 30, fontSize: 11 }, tickLabels: { fontSize: 8 } };
  return (
    <VictoryChart
      height={250}
      scale={{ x: "time", y: "linear" }}
      style={{ parent: { height: "100%", background: "white" } }}
      theme={VictoryTheme.material}
      width={750}
    >
      <VictoryLabel x={375} y={20} text={props.title} textAnchor="middle" />
      <VictoryAxis
        label={"Time"}
        style={axisStyle} />
      <VictoryAxis
        dependentAxis
        domain={[0, max_y]}
        label={props.unit}
        style={axisStyle}
        tickFormat={(t) => `${readableNumber(t)}`} />
      <Background data={{ green: green, grey: grey, yellow: yellow, red: red }} />
      <VictoryLine
        data={measurements}
        interpolation="stepBefore"
        style={{ data: { stroke: "black", strokeWidth: 2 } }} />
    </VictoryChart>
  )
}
