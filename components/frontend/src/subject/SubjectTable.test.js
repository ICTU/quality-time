import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { DataModel } from '../context/DataModel';
import { SubjectTable } from './SubjectTable';

const metric = {
    unit: "testUnit",
    scale: "count",
    type: "metric_type",
    name: "name_1",
    tags: ["Tag 1"]
}
const metric2 = {
    unit: "tests",
    scale: "percentage",
    name: "name_2",
    type: "metric_type",
}
const datamodel = {
    metrics: {
        metric_type: { name: "Metric type", tags: [] }
    },
    subjects: {
        subject_type: { metrics: ["metric_type"]}
    }
}
const reportDate = new Date("2020-01-15T00:00:00+00:00")

function renderSubjectTable(dates, hiddenColumns, visibleDetailsTabs) {
    const toggleVisibleDetailsTab = jest.fn();
    render(
        <DataModel.Provider value={datamodel}>
            <SubjectTable
                dates={dates ?? []}
                reportDate={reportDate}
                report={{ report_uuid: "report_uuid", subjects: { subject_uuid: { type: "subject_type", metrics: { 1: metric, 2: metric2 } } } }}
                measurements={
                    [
                        { metric_uuid: "1", start: "2020-01-14T00:00:00+00:00", end: "2020-01-15T00:00:00+00:00" },
                        { metric_uuid: "1", start: "2020-01-15T00:00:00+00:00", end: "2020-01-16T00:00:00+00:00" },
                        { metric_uuid: "2", start: "2020-01-10T00:00:00+00:00", end: "2020-01-10T00:00:00+00:00" },
                        { metric_uuid: "3", start: "2020-01-14T00:00:00+00:00", end: "2020-01-15T00:00:00+00:00" },
                    ]
                }
                metricEntries={Object.entries({ 1: metric, 2: metric2 })}
                subject={{ type: "subject_type", metrics: { 1: metric, 2: metric2 } }}
                subject_uuid="subject_uuid"
                hiddenColumns={hiddenColumns ?? []}
                toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                visibleDetailsTabs={visibleDetailsTabs ?? []}
            />
        </DataModel.Provider>
    );
    return toggleVisibleDetailsTab
}

it('displays all the metrics', () => {
    renderSubjectTable()
    const metricNames = ["name_1", "name_2"]
    metricNames.forEach(metricName => {
        expect(screen.queryAllByText(metricName).length).toBe(1)
    })
});

it('shows the date columns', () => {
    const dates = [
        new Date("2020-01-15T00:00:00+00:00"),
        new Date("2020-01-14T00:00:00+00:00"),
        new Date("2020-01-13T00:00:00+00:00"),
    ]
    renderSubjectTable(dates)
    dates.forEach((date) => {
        expect(screen.queryAllByText(date.toLocaleDateString()).length).toBe(1)
    })
})

it('shows the source column', () => {
    renderSubjectTable()
    expect(screen.queryAllByText(/Source/).length).toBe(1)
})

it('hides the source column', () => {
    renderSubjectTable([], ["source"])
    expect(screen.queryAllByText(/Source/).length).toBe(0)
})

it('shows the comment column', () => {
    renderSubjectTable()
    expect(screen.queryAllByText(/Comment/).length).toBe(1)
})

it('hides the source column', () => {
    renderSubjectTable([], ["comment"])
    expect(screen.queryAllByText(/Comment/).length).toBe(0)
})

it('shows the issue column', () => {
    renderSubjectTable()
    expect(screen.queryAllByText(/Issues/).length).toBe(1)
})

it('hides the issue column', () => {
    renderSubjectTable([], ["issues"])
    expect(screen.queryAllByText(/Issues/).length).toBe(0)
})

it('shows the tags column', () => {
    renderSubjectTable()
    expect(screen.queryAllByText(/Tags/).length).toBe(1)
    expect(screen.queryAllByText(/Tag 1/).length).toBe(1)
})

it('hides the tags column', () => {
    renderSubjectTable([], ["tags"])
    expect(screen.queryAllByText(/Tags/).length).toBe(0)
    expect(screen.queryAllByText(/Tag 1/).length).toBe(0)
})

it('expands the details via the button', () => {
    const toggleVisibleDetailsTab = renderSubjectTable()
    const expand = screen.getAllByRole("button")[0];
    fireEvent.click(expand);
    expect(toggleVisibleDetailsTab).toHaveBeenCalledWith("1:0");
})

it('collapses the details via the button', () => {
    const toggleVisibleDetailsTab = renderSubjectTable([], [], ["1:0"])
    const expand = screen.getAllByRole("button")[0];
    fireEvent.click(expand);
    expect(toggleVisibleDetailsTab).toHaveBeenCalledWith("1:0");
})

it('expands the details via the url', () => {
    renderSubjectTable()
    expect(screen.queryAllByText("Configuration").length).toBe(0)
    renderSubjectTable([], [], ["1:0"])
    expect(screen.queryAllByText("Configuration").length).toBe(1)
})
