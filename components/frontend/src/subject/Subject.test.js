import { act, fireEvent, render } from "@testing-library/react";
import { Subject } from "./Subject";
import * as fetch_server_api from '../api/fetch_server_api';
import * as TrendTable from '../trendTable/TrendTable';
import * as SubjectDetails from './SubjectDetails';


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

it('can switch between measurements and subject details', async () => {

  jest.mock("../api/fetch_server_api.js")
  fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true, measurements: [] });
  
  await act(async () => {
    const { getByText, getByRole } = render(
      <Subject 
        datamodel={datamodel} 
        report={report} 
        subject_uuid="subject_uuid" 
        tags={[]} 
        hiddenColumns={[]}
        visibleDetailsTabs={[]} />);

    fireEvent.click(getByRole("listbox"));
    fireEvent.click(getByText("Trend table"));
  });

  expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", "subject/subject_uuid/measurements", undefined);
})

it('shows the subject title and subject details', async () => {

  // mock child components to check which one gets rendered
  jest.mock("./SubjectDetails")
  SubjectDetails.SubjectDetails = () => <tbody data-testid="subject-details"></tbody>
  jest.mock("../trendTable/TrendTable")
  TrendTable.TrendTable = () => <tbody data-testid="subject-table"></tbody>

  const { queryAllByText, queryAllByTestId } = render(
    <Subject 
      datamodel={datamodel} 
      report={report} 
      subject_uuid="subject_uuid" 
      tags={[]} 
      hiddenColumns={[]}
      visibleDetailsTabs={[]} />);

  expect(queryAllByText("Subject 1 title").length).toBe(1);
  expect(queryAllByTestId("subject-details").length).toBe(1)
})
