import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import { createTestableSettings } from "../__fixtures__/fixtures"
import * as fetchServerApi from "../api/fetch_server_api"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import {
    asyncClickButton,
    asyncClickText,
    clickLabeledElement,
    clickText,
    expectFetch,
    expectNoAccessibilityViolations,
    expectText,
} from "../testUtils"
import * as toast from "../widgets/toast"
import { Sources } from "./Sources"

const dataModel = {
    metrics: { metric_type: { sources: ["source_type1", "source_type2"] } },
    sources: {
        source_type1: {
            name: "Source type 1",
            parameters: { url: { type: "url", name: "URL", metrics: ["metric_type"] } },
        },
        source_type2: { name: "Source type 2", parameters: {} },
    },
}

const report = {
    subjects: {
        subject_uuid: {
            name: "Subject",
            metrics: {
                metric_uuid: {
                    name: "Metric",
                    type: "metric_type",
                    sources: {
                        source_uuid: {
                            name: "Source 1",
                            type: "source_type1",
                            parameters: { url: "https://test.nl" },
                        },
                        non_existing_source_type: {
                            name: "Source with non-existing source type",
                            type: "non-existing",
                        },
                    },
                },
                other_metric_uuid: {
                    name: "Other metric",
                    type: "metric_type",
                    sources: { other_source_uuid: { name: "Source 2", type: "source_type2" } },
                },
                metric_without_sources: {
                    name: "Metric without sources",
                    type: "metric_type",
                    sources: {},
                },
                metric_with_two_sources: {
                    name: "Metric with two sources",
                    type: "metric_type",
                    sources: {
                        source_uuid1: {
                            name: "Source 3",
                            type: "source_type1",
                            parameters: { url: "https://test.nl" },
                        },
                        source_uuid2: {
                            name: "Source 4",
                            type: "source_type1",
                            parameters: { url: "https://test.nl" },
                        },
                    },
                },
            },
        },
    },
}

function renderSources(props) {
    return render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={dataModel}>
                <Sources
                    report={report}
                    reports={[report]}
                    metric={report.subjects.subject_uuid.metrics.metric_uuid}
                    metricUuid="metric_uuid"
                    measurement={{
                        sources: [{ source_uuid: "source_uuid", connection_error: "Oops" }],
                    }}
                    reload={vi.fn()}
                    settings={createTestableSettings()}
                    {...props}
                />
            </DataModel.Provider>
        </Permissions.Provider>,
    )
}

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true, nr_sources_mass_edited: 0 })
    vi.spyOn(toast, "showMessage")
})

it("shows a source", async () => {
    const { container } = renderSources()
    expect(screen.getAllByPlaceholderText(/Source type 1/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows a message if there are no sources", async () => {
    const { container } = renderSources({ metric: report.subjects.subject_uuid.metrics.metric_without_sources })
    expectText(/No sources have been configured/)
    await expectNoAccessibilityViolations(container)
})

it("doesn't show sources not in the data model", async () => {
    const { container } = renderSources()
    expect(screen.queryAllByDisplayValue(/Source 1/).length).toBe(1)
    expect(screen.queryAllByDisplayValue(/Source with non-existing source type/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("shows errored sources", async () => {
    const { container } = renderSources()
    expectText(/Connection error/)
    await expectNoAccessibilityViolations(container)
})

it("creates a new source", async () => {
    const { container } = renderSources()
    await asyncClickText(/Add source/)
    await expectNoAccessibilityViolations(container)
    await asyncClickText(/Source type 2/)
    expect(fetchServerApi.fetchServerApi).toHaveBeenNthCalledWith(1, "post", "source/new/metric_uuid", {
        type: "source_type2",
    })
    await expectNoAccessibilityViolations(container)
})

it("copies a source", async () => {
    const { container } = renderSources()
    await asyncClickText(/Copy source/)
    await expectNoAccessibilityViolations(container)
    await asyncClickText(/Source 1/)
    expect(fetchServerApi.fetchServerApi).toHaveBeenNthCalledWith(1, "post", "source/source_uuid/copy/metric_uuid", {})
    await expectNoAccessibilityViolations(container)
})

it("moves a source", async () => {
    const { container } = renderSources()
    await asyncClickText(/Move source/)
    await expectNoAccessibilityViolations(container)
    await asyncClickText(/Source 2/)
    expect(fetchServerApi.fetchServerApi).toHaveBeenNthCalledWith(
        1,
        "post",
        "source/other_source_uuid/move/metric_uuid",
        {},
    )
    await expectNoAccessibilityViolations(container)
})

it("updates a parameter of a source", async () => {
    const { container } = renderSources()
    await userEvent.type(screen.getByDisplayValue(/https:\/\/test.nl/), "https://other{Enter}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 15,
    })
    await expectNoAccessibilityViolations(container)
    await act(async () => {
        fireEvent.click(screen.getByDisplayValue("Source 1"))
    })
    expect(screen.getAllByDisplayValue("https://other").length).toBe(1)
    expectFetch("post", "source/source_uuid/parameter/url", { edit_scope: "source", url: "https://other" })
    expect(toast.showMessage).toHaveBeenCalledTimes(0)
    await expectNoAccessibilityViolations(container)
})

it("mass updates a parameter of a source", async () => {
    fetchServerApi.fetchServerApi.mockResolvedValue({ ok: true, nr_sources_mass_edited: 2 })
    const { container } = renderSources()
    clickLabeledElement(/Edit scope/)
    await expectNoAccessibilityViolations(container)
    clickText(/Apply change to subject/)
    expectText(/Apply change to subject/)
    await userEvent.type(screen.getByDisplayValue(/https:\/\/test.nl/), "https://other{Enter}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 15,
    })
    await expectNoAccessibilityViolations(container)
    await act(async () => {
        fireEvent.click(screen.getByDisplayValue("Source 1"))
    })
    expect(screen.getAllByDisplayValue("https://other").length).toBe(1)
    expectFetch("post", "source/source_uuid/parameter/url", { edit_scope: "subject", url: "https://other" })
    expect(toast.showMessage).toHaveBeenCalledTimes(1)
    await expectNoAccessibilityViolations(container)
})

it("repositions a source", async () => {
    renderSources({ metric: report.subjects.subject_uuid.metrics.metric_with_two_sources })
    await asyncClickButton(/Move source to the last position/, 0)
    expectFetch("post", "source/source_uuid1/attribute/position", { position: "last" })
})
