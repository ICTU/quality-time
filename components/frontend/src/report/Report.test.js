import React from 'react';
import { mount } from 'enzyme';
import { Report } from './Report';

let mockHistory = { location: {}, replace: () => { } };
const datamodel = { subjects: { subject_type: { name: "Subject type", metrics: ['metric_type'] } }, metrics: { metric_type: { tags: [] } } }
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
        metric_uuid: { type: "metric_type", tags: ["tag"], recent_measurements: [] }
      }
    }
  }
};

function create_report(report_json) {
  return (
    mount(
      <Report
        history={mockHistory}
        datamodel={datamodel}
        reports={[report_json]}
        report={report_json}
      />
    )
  )
}

describe("<Report />", () => {
  it('shows the report', () => {
    const wrapper = create_report(report);
    expect(wrapper.find("ReportTitle").prop("report")).toBe(report)
  });
  it('shows an error message if there is no report', () => {
    const wrapper = create_report();
    expect(wrapper.find("MessageHeader").childAt(0).text()).toBe("Sorry, this report doesn't exist")
  });
  it('hides columns', () => {
    const wrapper = create_report(report);
    expect(wrapper.find("Subject").prop("hiddenColumns")).toStrictEqual([]);
    wrapper.find("Subject").find("SubjectTableHeader").find("HamburgerHeader").find("ColumnMenuItem").at(0).find("DropdownItem").simulate("click");
    expect(wrapper.find("Subject").prop("hiddenColumns")).toStrictEqual(['trend'])
    wrapper.find("Subject").find("SubjectTableHeader").find("HamburgerHeader").find("ColumnMenuItem").at(0).find("DropdownItem").simulate("click");
    expect(wrapper.find("Subject").prop("hiddenColumns")).toStrictEqual([]);
  });
  it('hides columns on load', () => {
    mockHistory.location.search = "?hidden_columns=trend"
    const wrapper = create_report(report);
    expect(wrapper.find("Subject").prop("hiddenColumns")).toStrictEqual(['trend'])
    wrapper.find("Subject").find("SubjectTableHeader").find("HamburgerHeader").find("ColumnMenuItem").at(0).find("DropdownItem").simulate("click");
    expect(wrapper.find("Subject").prop("hiddenColumns")).toStrictEqual([]);
  });
  it('hides multiple columns on load', () => {
    mockHistory.location.search = "?hidden_columns=trend,tags"
    const wrapper = create_report(report);
    expect(wrapper.find("Subject").prop("hiddenColumns")).toStrictEqual(['trend', 'tags'])
    wrapper.find("Subject").find("SubjectTableHeader").find("HamburgerHeader").find("ColumnMenuItem").at(0).find("DropdownItem").simulate("click");
    expect(wrapper.find("Subject").prop("hiddenColumns")).toStrictEqual(['tags']);
  });
  it('can handle missing columns', () => {
    mockHistory.location.search = "?hidden_columns="
    const wrapper = create_report(report);
    expect(wrapper.find("Subject").prop("hiddenColumns")).toStrictEqual([])
  });
});
