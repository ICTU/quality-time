import React from 'react';
import { mount } from 'enzyme';
import { Subject } from './Subject';

const report = {subjects: {subject_uuid: {name: "Subject title", metrics: []}}};

describe("<Subject />", () => {
  it('shows the subject title', () => {
      const wrapper = mount(<Subject datamodel={{subjects: []}} report={report} subject_uuid="subject_uuid" />);
      expect(wrapper.find("SubjectTitle").find("HeaderContent").text()).toStrictEqual("Subject title");
  });
  it('changes the sort column when clicked', () => {
      const wrapper = mount(<Subject datamodel={{subjects: []}} report={report} subject_uuid="subject_uuid" />);
      expect(wrapper.find("TableHeaderCell").at(1).prop("sorted")).toBe(null);
      wrapper.find("TableHeaderCell").at(1).simulate("click");
      expect(wrapper.find("TableHeaderCell").at(1).prop("sorted")).toBe("ascending");
      wrapper.find("TableHeaderCell").at(1).simulate("click");
      expect(wrapper.find("TableHeaderCell").at(1).prop("sorted")).toBe("descending");
      wrapper.find("TableHeaderCell").at(1).simulate("click");
      expect(wrapper.find("TableHeaderCell").at(1).prop("sorted")).toBe(null);
  });
});