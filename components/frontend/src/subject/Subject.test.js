import React from 'react';
import { act } from 'react-dom/test-utils';
import { mount, shallow } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { Subject } from './Subject';
import * as fetch_server_api from '../api/fetch_server_api';

jest.mock("../api/fetch_server_api.js")

const datamodel = {
  subjects: {
    subject_type: { name: "Subject type", metrics: ["metric_type"] }
  },
  metrics: {
    metric_type: { name: "Metric type", tags: [] }
  }
}
const report = {
  subjects: {
    subject_uuid: {
      type: "subject_type", name: "Subject 1 title", metrics: {
        metric_uuid: {
          name: "M1", type: "metric_type", tags: [], sources: {}, recent_measurements: []
        },
        metric_uuidi2: {
          name: "M2", type: "metric_type", tags: [], sources: {}, recent_measurements: []
        }
      }
    },
    subject_uuid2: {
      type: "subject_type", name: "Subject 2 title", metrics: {
        metric_uuid3: {
          name: "M3", type: "metric_type", tags: [], sources: {}, recent_measurements: []
        }
      }
    }
  }
};

it('shows the subject title', () => {
  const wrapper = shallow(<Subject datamodel={datamodel} report={report} subject_uuid="subject_uuid" tags={[]} visibleDetailsTabs={[]} />);
  expect(wrapper.find("SubjectTitle").length).toBe(1);
});
it('shows the add subject button', () => {
  const wrapper = mount(
    <ReadOnlyContext.Provider value={false}>
      <Subject datamodel={datamodel} hiddenColumns={[]} report={report} reports={[report]} subject_uuid="subject_uuid" tags={[]} visibleDetailsTabs={[]} />
    </ReadOnlyContext.Provider>
  );
  expect(wrapper.find("AddButton").length).toBe(1);
});
it('changes the sort column when clicked', () => {
  function table_header_cell(index) {
    return wrapper.find("SubjectTableHeader").at(0).dive().find("SortableHeader").at(index).dive().find("TableHeaderCell");
  }
  const wrapper = shallow(<Subject datamodel={datamodel} hiddenColumns={[]} report={report} subject_uuid="subject_uuid" tags={[]} visibleDetailsTabs={[]} />);
  for (let index of [0, 1, 2, 3, 4, 5, 6]) {
    expect(table_header_cell(index).prop("sorted")).toBe(null);
    table_header_cell(index).simulate("click");
    expect(table_header_cell(index).prop("sorted")).toBe("ascending");
    table_header_cell(index).simulate("click");
    expect(table_header_cell(index).prop("sorted")).toBe("descending");
    table_header_cell(index).simulate("click");
    expect(table_header_cell(index).prop("sorted")).toBe(null);
  }
});
function click_metric(wrapper, button) {
  wrapper.find(button).find("div.button").simulate('click');
  wrapper.find(button).find("DropdownItem").at(0).simulate("click")
}
it('copies a metric when the copy button is clicked and a metric is selected', () => {
  fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
  const wrapper = mount(
    <ReadOnlyContext.Provider value={false}>
      <Subject datamodel={datamodel} hiddenColumns={[]} report={report} reports={[report]} subject_uuid="subject_uuid" tags={[]} visibleDetailsTabs={[]} />
    </ReadOnlyContext.Provider>);
  click_metric(wrapper, "CopyButton");
  expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("post", "metric/metric_uuid/copy/subject_uuid", {});
});
it('moves a metric when the move button is clicked and a metric is selected', async () => {
  fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
  const wrapper = mount(
    <ReadOnlyContext.Provider value={false}>
      <Subject datamodel={datamodel} hiddenColumns={[]} report={report} reports={[report]} subject_uuid="subject_uuid" tags={[]} visibleDetailsTabs={[]} />
    </ReadOnlyContext.Provider>)
  click_metric(wrapper, "MoveButton");
  expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("post", "metric/metric_uuid3/move/subject_uuid", {});
});