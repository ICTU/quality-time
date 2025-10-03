import { render } from "@testing-library/react"
import history from "history/browser"

import { createTestableSettings, dataModel, report } from "../__fixtures__/fixtures"
import { DataModel } from "../context/DataModel"
import { expectNoAccessibilityViolations, expectNoText, expectText } from "../testUtils"
import { Subjects } from "./Subjects"

function renderSubjects(reports) {
    const settings = createTestableSettings()
    return render(
        <DataModel.Provider value={dataModel}>
            <Subjects
                dates={[]}
                history={history}
                measurements={[]}
                reports={reports}
                reportsToShow={reports}
                settings={settings}
                tags={[]}
            />
        </DataModel.Provider>,
    )
}

beforeEach(() => {
    history.push("")
})

it("shows the subjects", async () => {
    const { container } = renderSubjects([report])
    expectText(/Subject/, 2)
    await expectNoAccessibilityViolations(container)
})

it("does not render invisible subjects", async () => {
    const report2 = {
        report_uuid: "report_uuid2",
        subjects: {
            subject_uuid2_1: {
                type: "subject_type",
                name: "Report 2 Subject 1 title",
                metrics: {
                    metric_uuid2_1: {
                        name: "M2_1",
                        type: "metric_type",
                        tags: [],
                        sources: {},
                        recent_measurements: [],
                    },
                },
            },
            subject_uuid2_2: {
                type: "subject_type",
                name: "Report 2 Subject 2 title",
                metrics: {
                    metric_uuid2_3: {
                        name: "M2_3",
                        type: "metric_type",
                        tags: [],
                        sources: {},
                        recent_measurements: [],
                    },
                },
            },
            subject_uuid2_3: {
                type: "subject_type",
                name: "Report 2 Subject 3 title",
                metrics: {
                    metric_uuid2_4: {
                        name: "M2_4",
                        type: "metric_type",
                        tags: [],
                        sources: {},
                        recent_measurements: [],
                    },
                },
            },
        },
        title: "Report 2 title",
    }
    const { container } = renderSubjects([report, report2])
    expectText(/Report 2 Subject 1/)
    expectText(/Report 2 Subject 2/)
    expectNoText(/Report 2 Subject 3/)
    await expectNoAccessibilityViolations(container)
})
