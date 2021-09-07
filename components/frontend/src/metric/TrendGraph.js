import React from 'react';
import { VictoryAxis, VictoryChart, VictoryLabel, VictoryLine, VictoryTheme, VictoryArea, VictoryStack } from 'victory';
import { nice_number, scaled_number } from '../utils';

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

export function TrendGraph({ measurements, scale, unit, title }) {
  let measurement_values = [];
  let target_values = [];
  let near_target_values = [];
  let debt_target_values = [];

  function measurement_attribute_as_number(measurement, field) {
    const value = (measurement[scale] && measurement[scale][field]) || null;
    return value !== null ? Number(value) : null;
  }

  measurements.forEach((measurement) => {
    measurement_values.push(measurement_attribute_as_number(measurement, "value"));
    target_values.push(measurement_attribute_as_number(measurement, "target"));
    near_target_values.push(measurement_attribute_as_number(measurement, "near_target"));
    debt_target_values.push(measurement_attribute_as_number(measurement, "debt_target"));
  });
  let max_y = nice_number(Math.max(
    Math.max(...measurement_values), Math.max(...target_values),
    Math.max(...near_target_values), Math.max(...debt_target_values)));

  // The colors of the background areas in the right order for "<" metrics, where lower values are better, and for
  // ">" metrics, where higher values are better:
  const colors = { "<": ["green", "grey", "yellow", "red"], ">": ["red", "yellow", "grey", "green"] };
  // The areas for each direction and each color. The lists will be filled with points (x, y0, and y) below:
  let areas = { "<": { green: [], grey: [], yellow: [], red: [] }, ">": { green: [], grey: [], yellow: [], red: [] } };
  let measurementValues = [];  // The measurement values (x, y)
  measurements.forEach((measurement, index) => {
    const x1 = new Date(measurement.start);
    const x2 = new Date(measurement.end);
    measurementValues.push({ y: measurement_values[index], x: x1 }, { y: measurement_values[index], x: x2 });
    if (target_values[index] === null) { return }  // Old measurements don't have target, near target and debt values
    let point = { green: { x: x1 }, grey: { x: x1 }, yellow: { x: x1 }, red: { x: x1 } };
    const absolute_y_values = {
      "<": {
        green: target_values[index],
        grey: debt_target_values[index] ?? 0,
        yellow: near_target_values[index],
        red: max_y
      },
      ">": {
        red: Math.min(target_values[index], near_target_values[index], debt_target_values[index] ?? Number.MAX_SAFE_INTEGER),
        yellow: debt_target_values[index] ?? 0,
        grey: target_values[index],
        green: max_y
      }
    };
    const direction = measurement[scale].direction || "<";
    let y0 = 0;
    colors[direction].forEach((color) => {
      const y = Math.max(0, absolute_y_values[direction][color] - y0);
      point[color].y0 = y0;
      point[color].y = y;
      areas[direction][color].push(point[color]);
      y0 += y;
    });
    if (x1.getTime() !== x2.getTime()) {
      colors[direction].forEach((color) => areas[direction][color].push({ ...point[color], x: x2 }));
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
      <VictoryLabel x={375} y={20} text={title} textAnchor="middle" />
      <VictoryAxis
        label={"Time"}
        style={axisStyle}
        tickCount={16} />
      <VictoryAxis
        dependentAxis
        domain={[0, max_y]}
        label={unit}
        style={axisStyle}
        tickFormat={(t) => `${scaled_number(t)}`} />
      <Background data={background_data} />
      <VictoryLine
        data={measurementValues}
        interpolation="stepBefore"
        style={{ data: { stroke: "black", strokeWidth: 2 } }} />
    </VictoryChart>
  )
}
