import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
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
  const wrapper = shallow(<Subject datamodel={datamodel} hiddenColumns={[]} report={report} subject_uuid="subject_uuid" tags={[]} visibleDetailsTabs={[]} />);
  const sortableHeaders = wrapper.find("SubjectDetails").dive().find("SubjectTableHeader").dive().find("SortableHeader");
  sortableHeaders.forEach(sortableHeader => {
    const tableHeaderCell = sortableHeader.dive().find("TableHeaderCell")
    expect(tableHeaderCell.prop("sorted")).toBe(null);
    tableHeaderCell.simulate("click");
    expect(tableHeaderCell.prop("sorted")).toBe("ascending");
    tableHeaderCell.simulate("click");
    expect(tableHeaderCell.prop("sorted")).toBe("descending");
    tableHeaderCell.simulate("click");
    expect(tableHeaderCell.prop("sorted")).toBe(null);
  })
});

it('copies a metric when the copy button is clicked and a metric is selected', async () => {
  fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
  await act(async () => {
    render(
      <ReadOnlyContext.Provider value={false}>
        <Subject datamodel={datamodel} hiddenColumns={[]} report={report} reports={[report]} subject_uuid="subject_uuid" tags={[]} visibleDetailsTabs={[]} />
      </ReadOnlyContext.Provider>);
    fireEvent.click(screen.getByText(/Copy metric/));
  });
  await act(async () => {
    fireEvent.click(screen.getAllByText(/M1/)[1]);
  });
  expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("post", "metric/metric_uuid/copy/subject_uuid", {});
});

it('moves a metric when the move button is clicked and a metric is selected', async () => {
  fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
  await act(async () => {
    render(
      <ReadOnlyContext.Provider value={false}>
        <Subject datamodel={datamodel} hiddenColumns={[]} report={report} reports={[report]} subject_uuid="subject_uuid" tags={[]} visibleDetailsTabs={[]} />
      </ReadOnlyContext.Provider>)
    fireEvent.click(screen.getByText(/Move metric/));
  });
  await act(async () => {
    fireEvent.click(screen.getByText(/Subject 2 title/));
  })
  expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("post", "metric/metric_uuid3/move/subject_uuid", {});
});