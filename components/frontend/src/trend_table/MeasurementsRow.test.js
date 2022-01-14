import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { MeasurementsRow } from './MeasurementsRow';
import { DataModel } from '../context/DataModel';

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

    const dataModel = { metrics: { metricType: { name: "testName", unit: "" } } }
    const visibleDetailsTabs = [];
    const toggleVisibleDetailsTab = jest.fn();

    function render_measurements_row(metric) {
        return render(
            <table>
                <tbody>
                    <DataModel.Provider value={dataModel}>
                        <MeasurementsRow
                            metric_uuid="metric_uuid"
                            metric={metric}
                            report={{subjects: {subject_uuid: {metrics: {metric_uuid: {type: "metricType"}}}}}}
                            subject_uuid="subject_uuid"
                            measurements={measurements}
                            dates={dates}
                            reportDate={null}
                            hiddenColumns={[]}
                            visibleDetailsTabs={visibleDetailsTabs}
                            toggleVisibleDetailsTab={(tab) => toggleVisibleDetailsTab(tab)}
                        />
                    </DataModel.Provider>
                </tbody>
            </table>
        );
    }

    it('renders one single row with metric name, measurement values and unit', () => {
        const { queryAllByText } = render_measurements_row({ type: "metricType", unit: "testUnit", scale: "count", recent_measurements: [] })
        expect(queryAllByText("testName").length).toBe(1) // measurement name cell
        expect(queryAllByText("?").length).toBe(1) // first date before first measurement
        expect(queryAllByText("0").length).toBe(1) // two cells with measurements
        expect(queryAllByText("1").length).toBe(1) // two cells with measurements
        expect(queryAllByText("testUnit").length).toBe(1)
    });

    it('renders one single row with metric name, measurement values and minutes unit', () => {
        dataModel.metrics.metricType.unit = "minutes"
        const { queryAllByText } = render_measurements_row({ type: "metricType", unit: "", scale: "count", recent_measurements: [] })
        expect(queryAllByText("testName").length).toBe(1) // measurement name cell
        expect(queryAllByText("?").length).toBe(1) // first date before first measurement
        expect(queryAllByText("0:00").length).toBe(1) // two cells with measurements
        expect(queryAllByText("0:01").length).toBe(1) // two cells with measurements
        expect(queryAllByText("hours").length).toBe(1)
    });

    it('expands and collapses the metric via the props', () => {
        render_measurements_row({ type: "metricType", unit: "testUnit", scale: "count", recent_measurements: [] })
        expect(screen.queryAllByText("Configuration").length).toBe(0)
        visibleDetailsTabs.push("metric_uuid:0")
        render_measurements_row({ type: "metricType", unit: "testUnit", scale: "count", recent_measurements: [] })
        expect(screen.queryAllByText("Configuration").length).toBe(1)
    });

    it('expands and collapses the metric via the button', () => {
        render_measurements_row({ type: "metricType", unit: "testUnit", scale: "count", recent_measurements: [] })
        const expand = screen.getAllByRole("button")[0];
        fireEvent.click(expand);
        expect(toggleVisibleDetailsTab).toHaveBeenCalledWith("metric_uuid:0");
    });

})
