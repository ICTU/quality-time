import React from 'react';
import { mount } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { MeasurementDetails } from './MeasurementDetails';
import * as metric_api from '../api/metric';

jest.mock("../api/metric.js");

const report = {
    report_uuid: "report_uuid",
    subjects: {
        subject_uuid: {
            name: "Metric",
            metrics: {
                metric_uuid: {
                    accept_debt: false,
                    tags: [],
                    type: "violations"
                }
            }
        }
    }
};

describe("<MeasurementDetails />", () => {
    it('calls the callback on click', () => {
        const mockCallBack = jest.fn();
        const wrapper = mount(
            <ReadOnlyContext.Provider value={false}>
                <MeasurementDetails
                    datamodel={{ metrics: { violations: { direction: "<", tags: [] } } }}
                    measurements={[]}
                    metric_uuid="metric_uuid"
                    report={report}
                    reports={[report]}
                    stop_sort={mockCallBack}
                    subject_uuid="subject_uuid"
                />
            </ReadOnlyContext.Provider>
        );
        wrapper.find({ icon: "angle double down" }).at(0).simulate("click");
        expect(mockCallBack).toHaveBeenCalled();
    });
    it('calls the callback on copy', () => {
        const wrapper = mount(
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
        expect(metric_api.copy_metric).toHaveBeenCalled();
    });
});
