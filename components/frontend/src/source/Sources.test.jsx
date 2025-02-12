import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetch_server_api from "../api/fetch_server_api"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
import * as toast from "../widgets/toast"
import { Sources } from "./Sources"

vi.mock("../api/fetch_server_api.js")
vi.mock("../widgets/toast.jsx")

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
                    metric_uuid="metric_uuid"
                    measurement={{
                        sources: [{ source_uuid: "source_uuid", connection_error: "Oops" }],
                    }}
                    reload={() => {
                        /* Dummy implemention */
                    }}
                    {...props}
                />
            </DataModel.Provider>
        </Permissions.Provider>,
    )
}

it("shows a source", async () => {
    const { container } = renderSources()
    expect(screen.getAllByPlaceholderText(/Source type 1/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows a message if there are no sources", async () => {
    const { container } = renderSources({ metric: report.subjects.subject_uuid.metrics.metric_without_sources })
    expect(screen.getAllByText(/No sources have been configured/).length).toBe(1)
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
    expect(screen.getAllByText(/Connection error/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("creates a new source", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    const { container } = renderSources()
    await act(async () => {
        fireEvent.click(screen.getByText(/Add source/))
    })
    await expectNoAccessibilityViolations(container)
    await act(async () => {
        fireEvent.click(screen.getByText(/Source type 2/))
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenNthCalledWith(1, "post", "source/new/metric_uuid", {
        type: "source_type2",
    })
    await expectNoAccessibilityViolations(container)
})

it("copies a source", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    const { container } = renderSources()
    await act(async () => {
        fireEvent.click(screen.getByText(/Copy source/))
    })
    await expectNoAccessibilityViolations(container)
    await act(async () => {
        fireEvent.click(screen.getByText(/Source 1/))
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenNthCalledWith(
        1,
        "post",
        "source/source_uuid/copy/metric_uuid",
        {},
    )
    await expectNoAccessibilityViolations(container)
})

it("moves a source", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    const { container } = renderSources()
    await act(async () => {
        fireEvent.click(screen.getByText(/Move source/))
    })
    await expectNoAccessibilityViolations(container)
    await act(async () => {
        fireEvent.click(screen.getByText(/Source 2/))
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenNthCalledWith(
        1,
        "post",
        "source/other_source_uuid/move/metric_uuid",
        {},
    )
    await expectNoAccessibilityViolations(container)
})

it("updates a parameter of a source", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true, nr_sources_mass_edited: 0 })
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
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("post", "source/source_uuid/parameter/url", {
        edit_scope: "source",
        url: "https://other",
    })
    expect(toast.showMessage).toHaveBeenCalledTimes(0)
    await expectNoAccessibilityViolations(container)
})

it("mass updates a parameter of a source", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true, nr_sources_mass_edited: 2 })
    const { container } = renderSources()
    fireEvent.click(screen.getByLabelText(/Edit scope/))
    await expectNoAccessibilityViolations(container)
    fireEvent.click(screen.getByText(/Apply change to subject/))
    expect(screen.getAllByText(/Apply change to subject/).length).toBe(1)
    await userEvent.type(screen.getByDisplayValue(/https:\/\/test.nl/), "https://other{Enter}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 15,
    })
    await expectNoAccessibilityViolations(container)
    await act(async () => {
        fireEvent.click(screen.getByDisplayValue("Source 1"))
    })
    expect(screen.getAllByDisplayValue("https://other").length).toBe(1)
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("post", "source/source_uuid/parameter/url", {
        edit_scope: "subject",
        url: "https://other",
    })
    expect(toast.showMessage).toHaveBeenCalledTimes(1)
    await expectNoAccessibilityViolations(container)
})
