import React from 'react';
import { render } from '@testing-library/react';
import { MeasurementsRow } from './MeasurementsRow';

describe("MeasurementRow", () => {

    const measurements = [
        {
            metric_uuid: "1",
            start: "2020-01-06T00:00:00+00:00",
            end: "2020-01-09T00:00:00+00:00",
            count: {
                value: "1",
                status: "near_target_met",
                target: "1",
            }
        },
        {
            metric_uuid: "0",
            start: "2020-01-04T00:00:00+00:00",
            end: "2020-01-06T00:00:00+00:00",
            count: {
                value: "0",
                status: "near_target_met",
                target: "0",
            }
        },
    ]
    const dates = [
        new Date("2020-01-09T00:00:00+00:00"),
        new Date("2020-01-05T00:00:00+00:00"),
        new Date("2020-01-03T00:00:00+00:00"),
    ]

    function render_measurements_row(metricType, metric) {
        return render(
            <table>
                <tbody>
                    <MeasurementsRow
                        datamodel={{metrics: {metricType: {unit: ""}}}}
                        metricType={metricType}
                        metricName="testName"
                        metric={metric}
                        measurements={measurements}
                        dates={dates}
                        visibleDetailsTabs={[]}
                    />
                </tbody>
            </table>
        );
    }

    it('renders one single row with metric name, measurement values and unit', () => {
        const { queryAllByText } = render_measurements_row({unit: "foo"}, {type: "metricType", unit: "testUnit", scale: "count", recent_measurements: []})
        expect(queryAllByText("testName").length).toBe(1) // measurement name cell
        expect(queryAllByText("?").length).toBe(1) // first date before first measurement
        expect(queryAllByText("0").length).toBe(1) // two cells with measurements
        expect(queryAllByText("1").length).toBe(1) // two cells with measurements
        expect(queryAllByText("testUnit").length).toBe(1)
    });

    it('renders one single row with metric name, measurement values and minutes unit', () => {
        const { queryAllByText } = render_measurements_row({unit: "minutes"}, {type: "metricType", unit: "", scale: "count", recent_measurements: []})
        expect(queryAllByText("testName").length).toBe(1) // measurement name cell
        expect(queryAllByText("?").length).toBe(1) // first date before first measurement
        expect(queryAllByText("0:00").length).toBe(1) // two cells with measurements
        expect(queryAllByText("0:01").length).toBe(1) // two cells with measurements
        expect(queryAllByText("hours").length).toBe(1)
    });
})
