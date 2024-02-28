import { render, screen } from "@testing-library/react";
import history from 'history/browser';
import { DataModel } from '../context/DataModel';
import { Subjects } from './Subjects';
import { createTestableSettings, datamodel, report } from "../__fixtures__/fixtures";

function renderSubjects(reports) {
    const settings = createTestableSettings()
    return render(
        <DataModel.Provider value={datamodel}>
            <Subjects
                dates={[]}
                history={history}
                measurements={[]}
                reports={reports}
                reportsToShow={reports}
                settings={settings}
                tags={[]}
            />
        </DataModel.Provider>
    )
}

beforeEach(() => {
    history.push("")
})

it("shows the subjects", () => {
    renderSubjects([report]);
    expect(screen.getAllByText(/Subject/).length).toBe(2);
})

it("does not render invisible subjects", () => {
    const report2 = {
        report_uuid: "report_uuid2",
        subjects: {
            subject_uuid2_1: {
                type: "subject_type", name: "Report 2 Subject 1 title", metrics: {
                    metric_uuid2_1: {
                        name: "M2_1", type: "metric_type", tags: [], sources: {}, recent_measurements: []
                    },
                }
            },
            subject_uuid2_2: {
                type: "subject_type", name: "Report 2 Subject 2 title", metrics: {
                    metric_uuid2_3: {
                        name: "M2_3", type: "metric_type", tags: [], sources: {}, recent_measurements: []
                    }
                }
            },
            subject_uuid2_3: {
                type: "subject_type", name: "Report 2 Subject 3 title", metrics: {
                    metric_uuid2_4: {
                        name: "M2_4", type: "metric_type", tags: [], sources: {}, recent_measurements: []
                    }
                }
            }
        },
        title: "Report 2 title"
    }
    renderSubjects([report, report2]);
    expect(screen.getAllByText(/Report 2 Subject 1/).length).toBe(1);
    expect(screen.getAllByText(/Report 2 Subject 2/).length).toBe(1);
    expect(screen.queryAllByText(/Report 2 Subject 3/).length).toBe(0);
})
