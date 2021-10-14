import React from 'react';
import { render } from '@testing-library/react';
import { TrendTable } from '../trend_table/TrendTable';
import { DataModel } from '../context/DataModel';

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

it('calculates column dates correctly', () => {
    const { queryAllByText } = render(
        <DataModel.Provider value={datamodel}>
            <TrendTable
                reportDate={reportDate}
                measurements={[]}
                metrics={{ 1: metric }}
                subject={{metrics: {1: metric}}}
                trendTableInterval={1}
                trendTableNrDates={3}
                setTrendTableInterval={() => {/*Dummy implementation*/ }}
                setTrendTableNrDates={() => {/*Dummy implementation*/ }}
                visibleDetailsTabs={[]}
            />
        </DataModel.Provider>

    );

    const expectedDates = [
        new Date("2020-01-01T00:00:00+00:00"),
        new Date("2020-01-08T00:00:00+00:00"),
        new Date("2020-01-15T00:00:00+00:00"),
    ]

    expectedDates.forEach(date => {
        expect(queryAllByText(date.toLocaleDateString()).length).toBe(1)
    })
});

it('displays all the metrics', () => {
    const { queryAllByText } = render(
        <DataModel.Provider value={datamodel}>
            <TrendTable
                reportDate={reportDate}
                measurements={[]}
                metrics={{ 1: metric, 2: metric2 }}
                subject={{metrics: {1: metric, 2: metric2}}}
                trendTableInterval={1}
                trendTableNrDates={3}
                setTrendTableInterval={() => {/*Dummy implementation*/ }}
                setTrendTableNrDates={() => {/*Dummy implementation*/ }}
                visibleDetailsTabs={[]}
            />
        </DataModel.Provider>
    );

    const metricNames = ["name_1", "name_2"]
    metricNames.forEach(metricName => {
        expect(queryAllByText(metricName).length).toBe(1)
    })
});
