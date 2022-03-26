import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { SubjectTableRow } from './SubjectTableRow';
import { DataModel } from '../context/DataModel';

describe("MeasurementRow", () => {

    const dataModel = { metrics: { metricType: { name: "testName", unit: "" } } }
    const visibleDetailsTabs = [];
    const toggleVisibleDetailsTab = jest.fn();

    function render_measurements_row(metric) {
        return render(
            <table>
                <tbody>
                    <DataModel.Provider value={dataModel}>
                        <SubjectTableRow
                            metric_uuid="metric_uuid"
                            metric={metric}
                            report={{report_uuid: "report_uuid", subjects: {subject_uuid: {metrics: {metric_uuid: {type: "metricType"}}}}}}
                            subject_uuid="subject_uuid"
                            reportDate={null}
                            nrDates={1}
                            toggleVisibleDetailsTab={(tab) => toggleVisibleDetailsTab(tab)}
                            visibleDetailsTabs={visibleDetailsTabs}
                        />
                    </DataModel.Provider>
                </tbody>
            </table>
        );
    }

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
