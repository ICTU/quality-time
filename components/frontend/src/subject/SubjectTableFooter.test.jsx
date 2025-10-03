import { Table } from "@mui/material"
import { render } from "@testing-library/react"
import { vi } from "vitest"

import { dataModel, report } from "../__fixtures__/fixtures"
import * as fetchServerApi from "../api/fetch_server_api"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { asyncClickText, clickText, expectFetch, expectNoAccessibilityViolations } from "../testUtils"
import { SubjectTableFooter } from "./SubjectTableFooter"

const stopFilteringAndSorting = vi.fn()

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true })
})

afterEach(() => vi.restoreAllMocks())

it("shows the add metric button and adds a metric when clicked", async () => {
    const { container } = render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={dataModel}>
                <Table>
                    <SubjectTableFooter
                        reports={[]}
                        subjectUuid="subject_uuid"
                        subject={report.subjects.subject_uuid}
                        stopFilteringAndSorting={stopFilteringAndSorting}
                    />
                </Table>
            </DataModel.Provider>
        </Permissions.Provider>,
    )
    clickText(/Add metric/)
    await expectNoAccessibilityViolations(container)
    clickText(/Metric type/)
    expect(stopFilteringAndSorting).toHaveBeenCalled()
    expectFetch("post", "metric/new/subject_uuid", { type: "metric_type" })
    await expectNoAccessibilityViolations(container)
})

it("copies a metric when the copy button is clicked and a metric is selected", async () => {
    const { container } = render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={dataModel}>
                <Table>
                    <SubjectTableFooter
                        subjectUuid="subject_uuid"
                        subject={report.subjects.subject_uuid}
                        reports={[report]}
                        stopFilteringAndSorting={stopFilteringAndSorting}
                    />
                </Table>
            </DataModel.Provider>
        </Permissions.Provider>,
    )
    clickText(/Copy metric/)
    await expectNoAccessibilityViolations(container)
    await asyncClickText(/M1/, 0)
    expectFetch("post", "metric/metric_uuid/copy/subject_uuid", {})
    await expectNoAccessibilityViolations(container)
})

it("moves a metric when the move button is clicked and a metric is selected", async () => {
    const { container } = render(
        <DataModel.Provider value={dataModel}>
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <Table>
                    <SubjectTableFooter
                        subjectUuid="subject_uuid"
                        subject={report.subjects.subject_uuid}
                        reports={[report]}
                        stopFilteringAndSorting={stopFilteringAndSorting}
                    />
                </Table>
            </Permissions.Provider>
        </DataModel.Provider>,
    )
    clickText(/Move metric/)
    await expectNoAccessibilityViolations(container)
    await asyncClickText(/Subject 2 title/)
    expectFetch("post", "metric/metric_uuid3/move/subject_uuid", {})
    await expectNoAccessibilityViolations(container)
})
