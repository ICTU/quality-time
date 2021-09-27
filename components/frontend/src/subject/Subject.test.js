import { act, render } from "@testing-library/react";
import { Subject } from "./Subject";
import * as fetch_server_api from '../api/fetch_server_api';
import * as TrendTable from '../trend_table/TrendTable';
import * as SubjectDetails from './SubjectDetails';
import { datamodel, report } from "../__fixtures__/fixtures";

it('fetches measurements', async () => {

  jest.mock("../api/fetch_server_api.js")
  fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true, measurements: [] });
  
  await act(async () => {
    render(
      <Subject 
        datamodel={datamodel} 
        report={report} 
        subject_uuid="subject_uuid" 
        tags={[]} 
        hiddenColumns={[]}
        subjectTrendTable={true}
        visibleDetailsTabs={[]} />);
  });

  expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", "subject/subject_uuid/measurements", undefined);
})

it('shows the subject title and subject details', async () => {

  // mock child components to check which one gets rendered
  jest.mock("./SubjectDetails")
  SubjectDetails.SubjectDetails = () => <table><tbody data-testid="subject-details"></tbody></table>
  jest.mock("../trend_table/TrendTable")
  TrendTable.TrendTable = () => <table><tbody data-testid="subject-table"></tbody></table>

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
