import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
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
                        datamodel={{ metrics: { metricType: { name: "testName", unit: "" } } }}
                        metricType={metricType}
                        metric_uuid="metric_uuid"
                        metric={metric}
                        report={{subjects: {subject_uuid: {metrics: {metric_uuid: {type: "metricType"}}}}}}
                        subject_uuid="subject_uuid"
                        measurements={measurements}
                        dates={dates}
                        reportDate={null}
                        visibleDetailsTabs={[]}
                        toggleVisibleDetailsTab={() => {/* Dummy implementation*/ }}
                    />
                </tbody>
            </table>
        );
    }

    it('renders one single row with metric name, measurement values and unit', () => {
        const { queryAllByText } = render_measurements_row({ unit: "foo" }, { type: "metricType", unit: "testUnit", scale: "count", recent_measurements: [] })
        expect(queryAllByText("testName").length).toBe(1) // measurement name cell
        expect(queryAllByText("?").length).toBe(1) // first date before first measurement
        expect(queryAllByText("0").length).toBe(1) // two cells with measurements
        expect(queryAllByText("1").length).toBe(1) // two cells with measurements
        expect(queryAllByText("testUnit").length).toBe(1)
    });

    it('renders one single row with metric name, measurement values and minutes unit', () => {
        const { queryAllByText } = render_measurements_row({ unit: "minutes", recent_measurements: measurements }, { type: "metricType", unit: "", scale: "count", recent_measurements: [] })
        expect(queryAllByText("testName").length).toBe(1) // measurement name cell
        expect(queryAllByText("?").length).toBe(1) // first date before first measurement
        expect(queryAllByText("0:00").length).toBe(1) // two cells with measurements
        expect(queryAllByText("0:01").length).toBe(1) // two cells with measurements
        expect(queryAllByText("hours").length).toBe(1)
    });

    it('expands and collapses the metric', () => {
        const { queryAllByText } = render_measurements_row({ unit: "foo" }, { type: "metricType", unit: "testUnit", scale: "count", recent_measurements: [] })
        const expand = screen.getByRole("button");
        fireEvent.click(expand);
        expect(queryAllByText("Configuration").length).toBe(1)
        fireEvent.click(expand);
        expect(queryAllByText("Configuration").length).toBe(0)
    });
})
