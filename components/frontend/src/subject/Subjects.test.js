import React from 'react';
import { shallow } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { Subjects } from './Subjects';

const datamodel = { subjects: { subject_type: { name: "Subject type"} }, metrics: { metric_type: { tags: [] } } }
const report = { subjects: { subject_uuid: { type: "subject_type", name: "Subject title", metrics: { metric_uuid: { type: "metric_type", tags: [] } } } } };

let mockHistory = { location: "" };

describe("<Subjects />", () => {
    beforeEach(() => { mockHistory["replace"] = jest.fn(); });
    it('shows the subjects', () => {
        const wrapper = shallow(<Subjects datamodel={datamodel} reports={[report]} report={report} tags={[]} history={mockHistory} hidden_columns={[]} hide_metrics_not_requiring_action={false} />);
        expect(wrapper.find("Subject").length).toBe(1);
    });
    it('shows the add subject button when editable', () => {
        const wrapper = shallow(<ReadOnlyContext.Provider value={false}>
            <Subjects datamodel={datamodel} reports={[report]} report={report} tags={[]} history={mockHistory} hidden_columns={[]} hide_metrics_not_requiring_action={false} />
        </ReadOnlyContext.Provider>);
        expect(wrapper.find("Subjects").dive().find("ReadOnlyOrEditable").dive().find("ContextConsumer").dive().find("AddButton").prop("item_type")).toStrictEqual("subject");
    });
    it('hides metrics not requiring action', () => {
        const wrapper = shallow(<Subjects datamodel={datamodel} reports={[report]} report={report} subject_uuid="subject_uuid" tags={[]} history={mockHistory} hidden_columns={[]} hide_metrics_not_requiring_action={false} />);
        expect(wrapper.find("Subject").prop("hideMetricsNotRequiringAction")).toBe(false);
        wrapper.find("Subject").dive().find("SubjectTableHeader").dive().find("HamburgerHeader").dive().find("DropdownItem").at(0).simulate("click");
        expect(wrapper.find("Subject").prop("hideMetricsNotRequiringAction")).toBe(true);
        wrapper.find("Subject").dive().find("SubjectTableHeader").dive().find("HamburgerHeader").dive().find("DropdownItem").at(0).simulate("click");
        expect(wrapper.find("Subject").prop("hideMetricsNotRequiringAction")).toBe(false);
      });
    it('hides columns', () => {
        const wrapper = shallow(<Subjects datamodel={datamodel} reports={[report]} report={report} subject_uuid="subject_uuid" tags={[]} history={mockHistory} hidden_columns={[]} hide_metrics_not_requiring_action={false} />);
        expect(wrapper.find("Subject").prop("hiddenColumns")).toStrictEqual([]);
        wrapper.find("Subject").dive().find("SubjectTableHeader").dive().find("HamburgerHeader").dive().find("ColumnMenuItem").at(0).dive().find("DropdownItem").simulate("click");
        expect(wrapper.find("Subject").prop("hiddenColumns")).toStrictEqual(['trend'])
        wrapper.find("Subject").dive().find("SubjectTableHeader").dive().find("HamburgerHeader").dive().find("ColumnMenuItem").at(0).dive().find("DropdownItem").simulate("click");
        expect(wrapper.find("Subject").prop("hiddenColumns")).toStrictEqual([]);
      });
});