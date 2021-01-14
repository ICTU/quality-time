import React from 'react';
import { render } from '@testing-library/react';
import { MeasurementsRow } from './MeasurementsRow';

describe("MeasurementRow", () => {

    const metric = {
        unit: "testUnit",
        scale: "count"
    }
    const measurements = [
        {
            metric_uuid: "1",
            start: "2020-01-04T00:00:00+00:00",
            end: "2020-01-06T00:00:00+00:00",
            count: {
                value: "value 0",
                status: "near_target_met",
                target: "target 0",
            }
        },
        {
            metric_uuid: "1",
            start: "2020-01-06T00:00:00+00:00",
            end: "2020-01-08T00:00:00+00:00",
            count: {
                value: "value 1",
                status: "near_target_met",
                target: "target_1",
            }
        },
    ]
    const dates = [
        new Date("2020-01-03T00:00:00+00:00"),
        new Date("2020-01-05T00:00:00+00:00"),
        new Date("2020-01-09T00:00:00+00:00"),
    ]

    it('Renders one single row with metric name, measurement values and unit', () => {
    
        const { queryAllByText } = render(
          <table><tbody><MeasurementsRow metricType={{}} metricName="testName" metric={metric} metricMeasurements={measurements} dates={dates} /></tbody></table>
        );
    
        expect(queryAllByText("testName").length).toBe(1) // measurement name cell
        expect(queryAllByText("?").length).toBe(1) // first date before first measurement
        expect(queryAllByText("value 0").length).toBe(1) // two cells with measurements
        expect(queryAllByText("value 1").length).toBe(1) // two cells with measurements
        expect(queryAllByText("testUnit").length).toBe(1)
      });

    it('Renders two rows, one with values and one with targets', () => {
    
        const { queryAllByText } = render(
        <table><tbody><MeasurementsRow metricType={{}} metricName="testName" metric={metric} metricMeasurements={measurements} dates={dates} showTargetRow/></tbody></table>
        );
        
        expect(queryAllByText("Measurement").length).toBe(1) // measurement name cell
        expect(queryAllByText("Target").length).toBe(1) // target name cell
        expect(queryAllByText("?").length).toBe(2) // first date before first measurement
        expect(queryAllByText("value 0").length).toBe(1) // two cells with measurements
        expect(queryAllByText("value 1").length).toBe(1) // two cells with measurements
        expect(queryAllByText("target 0").length).toBe(1) // two cells with targets
        expect(queryAllByText("target 1").length).toBe(1) // two cells with targets
        expect(queryAllByText("testUnit").length).toBe(2)
    });
})
