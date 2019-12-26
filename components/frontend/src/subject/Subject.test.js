import React from 'react';
import { shallow } from 'enzyme';
import { Subject } from './Subject';

const datamodel = { subjects: { subject_type: { name: "Subject type"} }, metrics: { metric_type: { tags: [] } } }
const report = { subjects: { subject_uuid: { type: "subject_type", name: "Subject title", metrics: { metric_uuid: { type: "metric_type", tags: [] } } } } };

describe("<Subject />", () => {
  it('shows the subject title', () => {
    const wrapper = shallow(<Subject datamodel={datamodel} report={report} subject_uuid="subject_uuid" tags={[]} />);
    expect(wrapper.find("SubjectTitle").length).toBe(1);
  });
  it('changes the sort column when clicked', () => {
    const wrapper = shallow(<Subject datamodel={datamodel} report={report} subject_uuid="subject_uuid" tags={[]} />);
    expect(wrapper.find("SortableHeader").at(0).dive().find("TableHeaderCell").prop("sorted")).toBe(null);
    wrapper.find("SortableHeader").at(0).dive().find("TableHeaderCell").simulate("click");
    expect(wrapper.find("SortableHeader").at(0).dive().find("TableHeaderCell").prop("sorted")).toBe("ascending");
    wrapper.find("SortableHeader").at(0).dive().find("TableHeaderCell").simulate("click");
    expect(wrapper.find("SortableHeader").at(0).dive().find("TableHeaderCell").prop("sorted")).toBe("descending");
    wrapper.find("SortableHeader").at(0).dive().find("TableHeaderCell").simulate("click");
    expect(wrapper.find("SortableHeader").at(0).dive().find("TableHeaderCell").prop("sorted")).toBe(null);
  });
});