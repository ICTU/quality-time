import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { ReadOnlyContext } from '../context/ReadOnly';
import * as source_api from '../api/source';
import { Source } from './Source';

jest.mock("../api/source.js");

const datamodel = {
    metrics: { metric_type: { sources: ["source_type"] } },
    sources: { source_type: { name: "Source type", parameters: {} } }
};
const source = { type: "source_type" };
const report = { report_uuid: "report_uuid", subjects: {} };

describe('<Source />', () => {
    it('invokes the callback on clicking delete', async () => {
        await act(async () => {
            render(
                <ReadOnlyContext.Provider value={false}>
                    <Source datamodel={datamodel} metric_type="metric_type" report={report} reports={[report]} source={source} />
                </ReadOnlyContext.Provider>
            );
            fireEvent.click(screen.getByText(/Delete source/));
        })
        expect(source_api.delete_source).toHaveBeenCalled();
    })
});
