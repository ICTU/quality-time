import React from 'react';
import { render, screen } from '@testing-library/react';
import { DataModel } from '../context/DataModel';
import { MeasurementSources } from './MeasurementSources';

const dataModel = { metrics: { metric_type: { sources: ["source_type"] } } }

it('renders one measurement source', () => {
    render(
        <DataModel.Provider value={dataModel}>
            <MeasurementSources metric={
                {
                    type: "metric_type",
                    sources: { source_uuid: { type: "source_type", name: "Source name" } },
                    latest_measurement: { sources: [{ source_uuid: "source_uuid" }] }
                }
            }
            />
        </DataModel.Provider>
    )
    expect(screen.getAllByText(/Source name/).length).toBe(1)
})

it('renders multiple measurement sources', () => {
    render(
        <DataModel.Provider value={dataModel}>
            <MeasurementSources metric={
                {
                    type: "metric_type",
                    sources: { source_uuid1: { type: "source_type", name: "Source name 1" }, source_uuid2: { type: "source_type", name: "Source name 2" } },
                    latest_measurement: { sources: [{ source_uuid: "source_uuid1" }, { source_uuid: "source_uuid2"}] }
                }
            }
            />
        </DataModel.Provider>
    )
    expect(screen.getAllByText(/Source name 1, Source name 2/).length).toBe(1)
})
