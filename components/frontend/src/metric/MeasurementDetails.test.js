import React from 'react';
import { act } from 'react-dom/test-utils';
import { mount } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { MeasurementDetails } from './MeasurementDetails';
import * as changelog_api from '../api/changelog';
import * as metric_api from '../api/metric';
import * as measurement_api from '../api/measurement';

jest.mock("../api/changelog.js");
jest.mock("../api/metric.js");
jest.mock("../api/measurement.js");
measurement_api.get_measurements.mockImplementation(() => Promise.resolve({ ok: true, measurements: [{ sources: [{}] }] }));
changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [] }));

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
                            type: "source_type",
                            entities: []
                        }
                    }
                }
            }
        }
    }
};

const data_model = {
    sources: {source_type: {parameters: {}}},
    metrics: { violations: { direction: "<", tags: [], sources: ["source_type"] } } }

describe("<MeasurementDetails />", () => {
    it('switches tabs', async () => {
        let wrapper;
        await act(async () => {
            wrapper = mount(
                <ReadOnlyContext.Provider value={false}>
                    <MeasurementDetails
                        datamodel={data_model}
                        metric_uuid="metric_uuid"
                        report={report}
                        reports={[report]}
                        subject_uuid="subject_uuid"
                    />
                </ReadOnlyContext.Provider>
            );
            wrapper.find("MenuItem").at(1).simulate('click');
            wrapper.setProps({})  // rerender
        });
        expect(wrapper.find("a.active").text()).toBe("Sources");
    });
    it('calls the callback on click', async () => {
        const mockCallBack = jest.fn();
        let wrapper;
        await act(async () => {
            wrapper = mount(
                <ReadOnlyContext.Provider value={false}>
                    <MeasurementDetails
                        datamodel={data_model}
                        metric_uuid="metric_uuid"
                        report={report}
                        reports={[report]}
                        stop_sort={mockCallBack}
                        subject_uuid="subject_uuid"
                    />
                </ReadOnlyContext.Provider>
            );
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
                        datamodel={data_model}
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
