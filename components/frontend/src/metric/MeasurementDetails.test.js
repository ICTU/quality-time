import React from 'react';
import { act } from 'react-dom/test-utils';
import { mount } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { MeasurementDetails } from './MeasurementDetails';
import * as metric_api from '../api/metric';
import * as measurement_api from '../api/measurement';

jest.mock("../api/metric.js");
jest.mock("../api/measurement.js");
measurement_api.get_measurements.mockImplementation(() => Promise.resolve({ ok: true, measurements: [] }));

const report = {
    report_uuid: "report_uuid",
    subjects: {
        subject_uuid: {
            name: "Metric",
            metrics: {
                metric_uuid: {
                    accept_debt: false,
                    tags: [],
                    type: "violations",
                    sources: {
                        source_uuid: {
                            entities: []
                        }
                    }
                }
            }
        }
    }
};

describe("<MeasurementDetails />", () => {
    it('calls the callback on click', async () => {
        const mockCallBack = jest.fn();
        let wrapper;
        await act(async () => {
            wrapper = mount(
                <ReadOnlyContext.Provider value={false}>
                    <MeasurementDetails
                        datamodel={{ metrics: { violations: { direction: "<", tags: [] } } }}
                        metric_uuid="metric_uuid"
                        report={report}
                        reports={[report]}
                        stop_sort={mockCallBack}
                        subject_uuid="subject_uuid"
                    />
                </ReadOnlyContext.Provider>
            );
            wrapper.update();
            wrapper.find({ icon: "angle double down" }).at(0).simulate("click");
        });
        expect(mockCallBack).toHaveBeenCalled();
        expect(measurement_api.get_measurements).toHaveBeenCalled();
    });
    it('calls the callback on copy', async () => {
        let wrapper;
        await act(async () => {
            wrapper = mount(
                <ReadOnlyContext.Provider value={false}>
                    <MeasurementDetails
                        datamodel={{ metrics: { violations: { direction: "<", tags: [] } } }}
                        measurements={[]}
                        metric_uuid="metric_uuid"
                        report={report}
                        reports={[report]}
                        subject_uuid="subject_uuid"
                    />
                </ReadOnlyContext.Provider>
            );
            wrapper.find("CopyButton").simulate("click");
        });
        expect(metric_api.copy_metric).toHaveBeenCalled();
    });
});
