import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { useSettings } from "../app_ui_settings"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
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

function SourcesWrapper({ props }) {
    const settings = useSettings()
    return (
        <PermissionsContext value={[EDIT_REPORT_PERMISSION]}>
            <DataModelContext value={dataModel}>
                <Sources
                    report={report}
                    reports={[report]}
                    metric={report.subjects.subject_uuid.metrics.metric_uuid}
                    metricUuid="metric_uuid"
                    measurement={{
                        sources: [{ source_uuid: "source_uuid", connection_error: "Oops" }],
                    }}
                    reload={vi.fn()}
                    settings={settings}
                    {...props}
                />
            </DataModelContext>
        </PermissionsContext>
    )
}

function renderSources(props) {
    return render(<SourcesWrapper props={props} />)
}

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true, nr_sources_mass_edited: 0 })
    vi.spyOn(toast, "showMessage")
})

it("has no accessibility violations", async () => {
    const { container } = renderSources()
    await expectNoAccessibilityViolations(container)
})

it("shows a source", async () => {
    renderSources()
    expect(screen.getAllByPlaceholderText(/Source type 1/).length).toBe(1)
})

it("shows a message if there are no sources", async () => {
    renderSources({ metric: report.subjects.subject_uuid.metrics.metric_without_sources })
    expectText(/No sources have been configured/)
})

it("doesn't show sources not in the data model", async () => {
    renderSources()
    expect(screen.queryAllByDisplayValue(/Source 1/).length).toBe(1)
    expect(screen.queryAllByDisplayValue(/Source with non-existing source type/).length).toBe(0)
})

it("shows errored sources", async () => {
    renderSources()
    expectText(/Connection error/)
})

it("creates a new source", async () => {
    renderSources()
    await asyncClickText(/Add source/)
    await asyncClickText(/Source type 2/)
    expect(fetchServerApi.fetchServerApi).toHaveBeenNthCalledWith(1, "post", "source/new/metric_uuid", {
        type: "source_type2",
    })
})

it("copies a source", async () => {
    renderSources()
    await asyncClickText(/Copy source/)
    await asyncClickText(/Source 1/)
    expect(fetchServerApi.fetchServerApi).toHaveBeenNthCalledWith(1, "post", "source/source_uuid/copy/metric_uuid", {})
})

it("moves a source", async () => {
    renderSources()
    await asyncClickText(/Move source/)
    await asyncClickText(/Source 2/)
    expect(fetchServerApi.fetchServerApi).toHaveBeenNthCalledWith(
        1,
        "post",
        "source/other_source_uuid/move/metric_uuid",
        {},
    )
})

it("updates a parameter of a source", async () => {
    renderSources()
    await userEvent.type(screen.getByDisplayValue(/https:\/\/test.nl/), "https://other{Enter}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 15,
    })
    await act(async () => {
        fireEvent.click(screen.getByDisplayValue("Source 1"))
    })
    expect(screen.getAllByDisplayValue("https://other").length).toBe(1)
    expectFetch("post", "source/source_uuid/parameter/url", { edit_scope: "source", url: "https://other" })
    expect(toast.showMessage).toHaveBeenCalledTimes(0)
})

it("mass updates a parameter of a source", async () => {
    fetchServerApi.fetchServerApi.mockResolvedValue({ ok: true, nr_sources_mass_edited: 2 })
    renderSources()
    clickLabeledElement(/Edit scope/)
    clickText(/Apply change to subject/)
    expectText(/Apply change to subject/)
    await userEvent.type(screen.getByDisplayValue(/https:\/\/test.nl/), "https://other{Enter}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 15,
    })
    await act(async () => {
        fireEvent.click(screen.getByDisplayValue("Source 1"))
    })
    expect(screen.getAllByDisplayValue("https://other").length).toBe(1)
    expectFetch("post", "source/source_uuid/parameter/url", { edit_scope: "subject", url: "https://other" })
    expect(toast.showMessage).toHaveBeenCalledTimes(1)
})

it("repositions a source", async () => {
    renderSources({ metric: report.subjects.subject_uuid.metrics.metric_with_two_sources })
    await asyncClickButton(/Move source to the last position/, 0)
    expectFetch("post", "source/source_uuid1/attribute/position", { position: "last" })
})
