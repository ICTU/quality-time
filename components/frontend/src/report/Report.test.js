import React from 'react';
import { mount } from 'enzyme';
import { Report } from './Report';

const datamodel = { subjects: { subject_type: { name: "Subject type"} }, metrics: { metric_type: { tags: [] } } }
const report = {
  summary_by_subject: {
    subject_uuid: {
      red: 0,
      green: 0,
      yellow: 0,
      grey: 0,
      white: 0
    }
  },
  summary_by_tag: {
    tag: {
      red: 0,
      green: 0,
      yellow: 0,
      grey: 0,
      white: 0
    }
  },
  subjects: {
    subject_uuid: {
      type: "subject_type", name: "Subject title", metrics: {
        metric_uuid: { type: "metric_type", tags: ["tag"], recent_measurements: [] } } } } };

describe("<Report />", () => {
  it('shows the report', () => {
    const wrapper = mount(<Report datamodel={datamodel} report={report} />);
    expect(wrapper.find("ReportTitle").prop("report")).toBe(report)
  });
  it('shows an error message if there is no report', () => {
    const wrapper = mount(<Report datamodel={datamodel} />);
    expect(wrapper.find("MessageHeader").childAt(0).text()).toBe("Sorry, this report doesn't exist")
  });
});
