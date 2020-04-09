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
      {data.map(({ area, color, direction }) =>
        <VictoryArea
          key={color + direction}
          data={area}
          interpolation="stepBefore"
          style={{ data: { fill: color, opacity: 0.7, strokeWidth: 0 } }} />
      )}
    </VictoryStack>
  )
}

export function TrendGraph(props) {
  let measurement_values = [];
  let target_values = [];
  let near_target_values = [];
  let debt_target_values = [];

  function measurement_attribute_as_number(measurement, field) {
    const value = (measurement[props.scale] && measurement[props.scale][field]) || null;
    return value !== null ? Number(value) : null;
  }

  props.measurements.forEach((measurement) => {
    measurement_values.push(measurement_attribute_as_number(measurement, "value"));
    target_values.push(measurement_attribute_as_number(measurement, "target"));
    near_target_values.push(measurement_attribute_as_number(measurement, "near_target"));
    debt_target_values.push(measurement_attribute_as_number(measurement, "debt_target"));
  });
  let max_y = Math.max(
    Math.max(...measurement_values), Math.max(...target_values),
    Math.max(...near_target_values), Math.max(...debt_target_values));
  if (max_y < 18) { max_y = 20 } else if (max_y < 45) { max_y = 50 } else if (max_y < 90) { max_y = 100 } else { max_y += 20 }

  // The colors of the background areas in the right order for "<" metrics, where lower values are better, and for
  // ">" metrics, where higher values are better:
  const colors = { "<": ["green", "yellow", "grey", "red"], ">": ["red", "yellow", "grey", "green"] };
  // The areas for each direction and each color. The lists will be filled with points (x, y0, and y) below:
  let areas = { "<": { green: [], grey: [], yellow: [], red: [] }, ">": { green: [], grey: [], yellow: [], red: [] } };
  let measurements = [];  // The measurement values (x, y)
  props.measurements.forEach((measurement, index) => {
    const x1 = new Date(measurement.start);
    const x2 = new Date(measurement.end);
    measurements.push({ y: measurement_values[index], x: x1 }, { y: measurement_values[index], x: x2 });
    let point = { green: { x: x1 }, grey: { x: x1 }, yellow: { x: x1 }, red: { x: x1 } };
    if (target_values[index] !== null) {
      const direction = measurement[props.scale].direction || "<";
      if (direction === "<") {
        point.green.y0 = 0;
        point.green.y = target_values[index];
        point.grey.y0 = point.green.y0 + point.green.y;
        point.grey.y = Math.max(0, (debt_target_values[index] ?? 0) - point.grey.y0);
        point.yellow.y0 = point.grey.y0 + point.grey.y;
        point.yellow.y = Math.max(0, near_target_values[index] - (point.grey.y + point.green.y));
        point.red.y0 = point.yellow.y0 + point.yellow.y;
        point.red.y = max_y - point.red.y0;
      } else {
        point.red.y0 = 0;
        point.red.y = Math.min(target_values[index], near_target_values[index], debt_target_values[index] ?? Number.MAX_SAFE_INTEGER);
        point.yellow.y0 = point.red.y0 + point.red.y;
        point.yellow.y = debt_target_values[index] !== null ? Math.max(0, debt_target_values[index] - point.yellow.y0) : Math.max(0, target_values[index] - near_target_values[index]);
        point.grey.y0 = point.yellow.y0 + point.yellow.y;
        point.grey.y = target_values[index] - (point.red.y + point.yellow.y);
        point.green.y0 = point.grey.y0 + point.grey.y;
        point.green.y = max_y - point.green.y0;
      }
      colors[direction].forEach((color) => areas[direction][color].push(point[color]));
      if (x1.getTime() !== x2.getTime()) {
        colors[direction].forEach((color) => areas[direction][color].push({ ...point[color], x: x2 }));
      }
    }
  });
  const rgb = { green: "rgb(30,148,78,0.7)", yellow: "rgb(253,197,54,0.7)", grey: "rgb(150,150,150,0.7)", red: "rgb(211,59,55,0.7)" };
  var background_data = [];
  ["<", ">"].forEach((direction) => {
    if (areas[direction].green.length > 0) {
      colors[direction].forEach((color) => background_data.push(
        { area: areas[direction][color], color: rgb[color], direction: direction }));
    }
  });

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
      <Background data={background_data} />
      <VictoryLine
        data={measurements}
        interpolation="stepBefore"
        style={{ data: { stroke: "black", strokeWidth: 2 } }} />
    </VictoryChart>
  )
}
