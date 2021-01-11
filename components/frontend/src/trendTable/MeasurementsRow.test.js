import React from 'react';
import { render, screen } from '@testing-library/react';
import { MeasurementsRow } from './MeasurementsRow';

it('Renders only measurements row', () => {

    const metric = {
        unit: "test"
    }
    const measurements = [
        {
            metric_uuid: "1",
            start: "2020-01-01T00:00:00+00:00",
            end: "2020-01-10T00:00:00+00:00",
            count: {
                value: 0,
                status: "near_target_met",
                target: "0",
            }
        },
        {
            metric_uuid: "1",
            start: "2020-01-10T00:00:00+00:00",
            end: "2020-01-20T00:00:00+00:00",
            count: {
                value: 0,
                status: "near_target_met",
                target: "0",
            }
        },
    ]
    const dates = [
        new Date("2020-01-05T00:00:00+00:00"),
        new Date("2020-01-15T00:00:00+00:00"),
        new Date("2020-01-25T00:00:00+00:00"),
    ]

    console.log(dates)

    render(
      <MeasurementsRow metricType={{}} metricName="testName" metric={metric} metricMeasurements={measurements} dates={dates} />
    );
  });