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
          data={area[direction]}
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

  for (var i = 0; i < props.measurements.length; i++) {
    const measurement = props.measurements[i];
    measurement_values.push(measurement_attribute_as_number(measurement, "value"));
    target_values.push(measurement_attribute_as_number(measurement, "target"));
    near_target_values.push(measurement_attribute_as_number(measurement, "near_target"));
    debt_target_values.push(measurement_attribute_as_number(measurement, "debt_target"));
  }
  let max_y = Math.max(
    Math.max(...measurement_values), Math.max(...target_values),
    Math.max(...near_target_values), Math.max(...debt_target_values));
  if (max_y < 18) { max_y = 20 } else if (max_y < 45) { max_y = 50 } else if (max_y < 90) { max_y = 100 } else { max_y += 20 }

  let measurements = [];
  let green = { "<": [], ">": [] };
  let grey = { "<": [], ">": [] };
  let yellow = { "<": [], ">": [] };
  let red = { "<": [], ">": [] };
  for (i = 0; i < props.measurements.length; i++) {
    const measurement = props.measurements[i];
    const x1 = new Date(measurement.start);
    const x2 = new Date(measurement.end);
    measurements.push({ y: measurement_values[i], x: x1 }, { y: measurement_values[i], x: x2 });
    let green_point = {x: x1};
    let grey_point = {x: x1};
    let yellow_point = {x : x1};
    let red_point = {x: x1};
    if (target_values[i] !== null) {
      const direction = measurement[props.scale].direction || "<";
      if (direction === "<") {
        green_point.y0 = 0;
        green_point.y = target_values[i];
        grey_point.y0 = green_point.y0 + green_point.y;
        grey_point.y = debt_target_values[i] !== null ? Math.max(0, debt_target_values[i] - green_point.y) : 0;
        yellow_point.y0 = grey_point.y0 + grey_point.y;
        yellow_point.y = Math.max(0, near_target_values[i] - (grey_point.y + green_point.y));
        red_point.y0 = yellow_point.y0 + yellow_point.y;
        red_point.y = max_y - red_point.y0;
      } else {
        red_point.y0 = 0;
        red_point.y = Math.min(target_values[i], near_target_values[i], debt_target_values[i] === null ? Number.MAX_SAFE_INTEGER : debt_target_values[i]);
        yellow_point.y0 = red_point.y0 + red_point.y;
        yellow_point.y = debt_target_values[i] !== null ? Math.max(0, debt_target_values[i] - yellow_point.y0) : Math.max(0, target_values[i] - near_target_values[i]);
        grey_point.y0 = yellow_point.y0 + yellow_point.y;
        grey_point.y = target_values[i] - (red_point.y + yellow_point.y);
        green_point.y0 = grey_point.y0 + grey_point.y;
        green_point.y = max_y - green_point.y0;
      }
      green[direction].push(green_point);
      grey[direction].push(grey_point);
      yellow[direction].push(yellow_point);
      red[direction].push(red_point);
      if (x1.getTime() !== x2.getTime()) {
        green[direction].push({...green_point, x: x2});
        grey[direction].push({...grey_point, x: x2 });
        yellow[direction].push({...yellow_point, x: x2});
        red[direction].push({...red_point, x: x2});
      }
    }
  }
  var background_data = [];
  if (green["<"].length > 0) {
    background_data.push(
      { area: green, color: "rgb(30,148,78,0.7)", direction: "<" },
      { area: yellow, color: "rgb(253,197,54,0.7)", direction: "<" },
      { area: grey, color: "rgb(150,150,150,0.7)", direction: "<" },
      { area: red, color: "rgb(211,59,55,0.7)", direction: "<" }
    )
  }
  if (green[">"].length > 0) {
    background_data.push(
      { area: red, color: "rgb(211,59,55,0.7)", direction: ">" },
      { area: yellow, color: "rgb(253,197,54,0.7)", direction: ">" },
      { area: grey, color: "rgb(150,150,150,0.7)", direction: ">" },
      { area: green, color: "rgb(30,148,78,0.7)", direction: ">" }
    )
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
      <Background data={background_data} />
      <VictoryLine
        data={measurements}
        interpolation="stepBefore"
        style={{ data: { stroke: "black", strokeWidth: 2 } }} />
    </VictoryChart>
  )
}
