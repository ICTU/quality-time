import React from 'react';
import { render, screen } from '@testing-library/react';
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
    }
}
const reportDate = new Date("2020-01-15T00:00:00+00:00")

function renderSubjectTable(dateInterval, dateOrder, hiddenColumns) {
    return render(
        <DataModel.Provider value={datamodel}>
            <SubjectTable
                dateInterval={dateInterval}
                dateOrder={dateOrder}
                reportDate={reportDate}
                report={{report_uuid: "report_uuid"}}
                measurements={[]}
                metricEntries={Object.entries({ 1: metric, 2: metric2 })}
                subject={{ metrics: { 1: metric, 2: metric2 } }}
                nrDates={3}
                setDateInterval={() => {/*Dummy implementation*/ }}
                setNrDates={() => {/*Dummy implementation*/ }}
                hiddenColumns={hiddenColumns ?? []}
                visibleDetailsTabs={[]}
            />
        </DataModel.Provider>

    );
}

it('calculates weekly column dates correctly', () => {
    renderSubjectTable(7)
    const expectedDates = [
        new Date("2020-01-01T00:00:00+00:00"),
        new Date("2020-01-08T00:00:00+00:00"),
        new Date("2020-01-15T00:00:00+00:00"),
    ]
    expectedDates.forEach(date => {
        expect(screen.queryAllByText(date.toLocaleDateString()).length).toBe(1)
    })
});

it('calculates daily column dates correctly', () => {
    renderSubjectTable(1, "ascending")
    const expectedDates = [
        new Date("2020-01-13T00:00:00+00:00"),
        new Date("2020-01-14T00:00:00+00:00"),
        new Date("2020-01-15T00:00:00+00:00"),
    ]
    const actualDates = screen.queryAllByText(/2020/);
    expectedDates.forEach((expectedDate, index) => {
        expect(actualDates[index]).toHaveTextContent(expectedDate.toLocaleDateString())
    })
});

it('sorts the column dates descending', () => {
    renderSubjectTable(1, "descending")
    const expectedDates = [
        new Date("2020-01-15T00:00:00+00:00"),
        new Date("2020-01-14T00:00:00+00:00"),
        new Date("2020-01-13T00:00:00+00:00"),
    ]
    const actualDates = screen.queryAllByText(/2020/);
    expectedDates.forEach((expectedDate, index) => {
        expect(actualDates[index]).toHaveTextContent(expectedDate.toLocaleDateString())
    })
});

it('displays all the metrics', () => {
    renderSubjectTable(7)
    const metricNames = ["name_1", "name_2"]
    metricNames.forEach(metricName => {
        expect(screen.queryAllByText(metricName).length).toBe(1)
    })
});

it('shows the source column', () => {
    renderSubjectTable(7)
    expect(screen.queryAllByText(/Source/).length).toBe(1)
})

it('hides the source column', () => {
    renderSubjectTable(7, "ascending", ["source"])
    expect(screen.queryAllByText(/Source/).length).toBe(0)
})

it('shows the comment column', () => {
    renderSubjectTable(7)
    expect(screen.queryAllByText(/Comment/).length).toBe(1)
})

it('hides the source column', () => {
    renderSubjectTable(7, "ascending", ["comment"])
    expect(screen.queryAllByText(/Comment/).length).toBe(0)
})

it('shows the issue column', () => {
    renderSubjectTable(7)
    expect(screen.queryAllByText(/Issues/).length).toBe(1)
})

it('hides the issue column', () => {
    renderSubjectTable(7, "ascending", ["issues"])
    expect(screen.queryAllByText(/Issues/).length).toBe(0)
})

it('shows the tags column', () => {
    renderSubjectTable(7)
    expect(screen.queryAllByText(/Tags/).length).toBe(1)
    expect(screen.queryAllByText(/Tag 1/).length).toBe(1)
})

it('hides the tags column', () => {
    renderSubjectTable(7, "ascending", ["tags"])
    expect(screen.queryAllByText(/Tags/).length).toBe(0)
    expect(screen.queryAllByText(/Tag 1/).length).toBe(0)
})
