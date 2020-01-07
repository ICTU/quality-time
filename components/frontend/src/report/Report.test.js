import React from 'react';
import { shallow } from 'enzyme';
import { Report } from './Report';

const datamodel = { subjects: { subject_type: { name: "Subject type"} }, metrics: { metric_type: { tags: [] } } }
const report = { subjects: { subject_uuid: { type: "subject_type", name: "Subject title", metrics: { metric_uuid: { type: "metric_type", tags: [] } } } } };

describe("<Report />", () => {
  it('shows the report', () => {
    const wrapper = shallow(<Report datamodel={datamodel} report={report} />);
    expect(wrapper.find("ReportTitle").prop("report")).toBe(report)
  });
  it('shows an error message if there is no report', () => {
    const wrapper = shallow(<Report datamodel={datamodel} />);
    expect(wrapper.dive().find("MessageHeader").childAt(0).text()).toBe("Sorry, this report doesn't exist")
  });
});