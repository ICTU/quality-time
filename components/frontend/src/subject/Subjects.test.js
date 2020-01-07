import React from 'react';
import { mount, shallow } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { Subjects } from './Subjects';

const datamodel = { subjects: { subject_type: { name: "Subject type"} }, metrics: { metric_type: { tags: [] } } }
const report = { subjects: { subject_uuid: { type: "subject_type", name: "Subject title", metrics: { metric_uuid: { type: "metric_type", tags: [] } } } } };

describe("<Subjects />", () => {
    it('shows the subjects', () => {
        const wrapper = shallow(<Subjects datamodel={datamodel} report={report} tags={[]} />);
        expect(wrapper.find("Subject").length).toBe(1);
    });
    it('shows the add subject button when editable', () => {
        const wrapper = shallow(<ReadOnlyContext.Provider value={false}>
            <Subjects datamodel={datamodel} report={report} tags={[]} />
        </ReadOnlyContext.Provider>);
        expect(wrapper.find("Subjects").dive().find("ReadOnlyOrEditable").dive().find("ContextConsumer").dive().find("AddButton").prop("item_type")).toStrictEqual("subject");
    });
    it('hides metrics not requiring action', () => {
        function popup() {
            return
        }
        const wrapper = shallow(<Subjects datamodel={datamodel} report={report} subject_uuid="subject_uuid" tags={[]} />);
        expect(wrapper.find("Subject").prop("hideMetricsNotRequiringAction")).toBe(false);
        mount(wrapper.find("Subject").dive().find("SubjectTableHeader").dive().find("Popup").prop("trigger")).find("button").simulate("click");
        expect(wrapper.find("Subject").prop("hideMetricsNotRequiringAction")).toBe(true);
        mount(wrapper.find("Subject").dive().find("SubjectTableHeader").dive().find("Popup").prop("trigger")).find("button").simulate("click");
        expect(wrapper.find("Subject").prop("hideMetricsNotRequiringAction")).toBe(false);
      });
});