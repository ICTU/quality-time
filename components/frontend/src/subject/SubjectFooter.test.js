import { act, fireEvent, render, screen } from "@testing-library/react";
import { Table } from "semantic-ui-react";
import { ReadOnlyContext } from "../context/ReadOnly";
import { SubjectFooter } from "./SubjectFooter";
import * as fetch_server_api from '../api/fetch_server_api';


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

const resetSort = jest.fn()

jest.mock("../api/fetch_server_api.js")
fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });

it('shows the add metric button and adds a metric when clicked', async () => {
    
    const { queryAllByText, getByText } = render(
      <ReadOnlyContext.Provider value={false}>
        <Table>
            <SubjectFooter 
                subjectUuid="subject_uuid" 
                subject={report.subjects.subject_uuid} 
                datamodel={datamodel} 
                resetSortColumn={resetSort} />
        </Table>
      </ReadOnlyContext.Provider>
    );
    expect(queryAllByText("Add metric").length).toBe(1);

    await act(async () => {
        fireEvent.click(getByText("Add metric"))
    });
    expect(resetSort).toBeCalled()
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("post", "metric/new/subject_uuid", {});
  });
  
  it('copies a metric when the copy button is clicked and a metric is selected', async () => {
    await act(async () => {
      render(
        <ReadOnlyContext.Provider value={false}>
            <Table>
                <SubjectFooter 
                    subjectUuid="subject_uuid" 
                    subject={report.subjects.subject_uuid} 
                    datamodel={datamodel} 
                    reports={[report]}
                    resetSortColumn={resetSort} />
            </Table>
       </ReadOnlyContext.Provider>);
      fireEvent.click(screen.getByText(/Copy metric/));
    });
    await act(async () => {
      fireEvent.click(screen.getAllByText(/M1/)[0]);
    });
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("post", "metric/metric_uuid/copy/subject_uuid", {});
  });
  
  it('moves a metric when the move button is clicked and a metric is selected', async () => {
    await act(async () => {
      render(
        <ReadOnlyContext.Provider value={false}>
            <Table>
                <SubjectFooter 
                    subjectUuid="subject_uuid" 
                    subject={report.subjects.subject_uuid} 
                    datamodel={datamodel} 
                    reports={[report]}
                    resetSortColumn={resetSort} />
            </Table>
        </ReadOnlyContext.Provider>)
      fireEvent.click(screen.getByText(/Move metric/));
    });
    await act(async () => {
      fireEvent.click(screen.getByText(/Subject 2 title/));
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("post", "metric/metric_uuid3/move/subject_uuid", {});
  });