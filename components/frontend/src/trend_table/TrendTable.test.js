import React from 'react';
import { render, screen } from '@testing-library/react';
import { DataModel } from '../context/DataModel';
import { TrendTable } from './TrendTable';

const metric = {
    unit: "testUnit",
    scale: "count",
    type: "metric_type",
    name: "name_1"
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

function renderTrendTable(trendTableInterval) {
    return render(
        <DataModel.Provider value={datamodel}>
            <TrendTable
                reportDate={reportDate}
                measurements={[]}
                metrics={{ 1: metric, 2: metric2 }}
                subject={{metrics: {1: metric, 2: metric2}}}
                trendTableInterval={trendTableInterval}
                trendTableNrDates={3}
                setTrendTableInterval={() => {/*Dummy implementation*/ }}
                setTrendTableNrDates={() => {/*Dummy implementation*/ }}
                visibleDetailsTabs={[]}
            />
        </DataModel.Provider>

    );
}

it('calculates weekly column dates correctly', () => {
    renderTrendTable(7)
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
    renderTrendTable(1)
    const expectedDates = [
        new Date("2020-01-13T00:00:00+00:00"),
        new Date("2020-01-14T00:00:00+00:00"),
        new Date("2020-01-15T00:00:00+00:00"),
    ]
    expectedDates.forEach(date => {
        expect(screen.queryAllByText(date.toLocaleDateString()).length).toBe(1)
    })
});

it('displays all the metrics', () => {
    renderTrendTable(7)
    const metricNames = ["name_1", "name_2"]
    metricNames.forEach(metricName => {
        expect(screen.queryAllByText(metricName).length).toBe(1)
    })
});
