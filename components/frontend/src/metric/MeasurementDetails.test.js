import React from 'react';
import { mount } from 'enzyme';
import { MeasurementDetails } from './MeasurementDetails';

const report = {
    report_uuid: "report_uuid",
    subjects: {
        subject_uuid: {
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
        const wrapper = mount(<MeasurementDetails
            datamodel={{ metrics: { violations: { direction: "<", tags: [] } } }}
            measurements={[]}
            metric_uuid="metric_uuid"
            report={report}
            stop_sort={mockCallBack}
            subject_uuid="subject_uuid"
        />);
        wrapper.find({icon: "angle double down"}).at(0).simulate("click");
        expect(mockCallBack).toHaveBeenCalled();
    });
});
