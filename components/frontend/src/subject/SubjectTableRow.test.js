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
                            details={<span>Details</span>}
                            metric_uuid="metric_uuid"
                            metric={metric}
                            subject_uuid="subject_uuid"
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
        expect(screen.queryAllByText("Details").length).toBe(0)
        visibleDetailsTabs.push("metric_uuid:0")
        render_measurements_row({ type: "metricType", unit: "testUnit", scale: "count", recent_measurements: [] })
        expect(screen.queryAllByText("Details").length).toBe(1)
    });

    it('expands and collapses the metric via the button', () => {
        render_measurements_row({ type: "metricType", unit: "testUnit", scale: "count", recent_measurements: [] })
        const expand = screen.getAllByRole("button")[0];
        fireEvent.click(expand);
        expect(toggleVisibleDetailsTab).toHaveBeenCalledWith("metric_uuid:0");
    });
})
