import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import { createTestableSettings, dataModel, report } from "../__fixtures__/fixtures"
import * as fetchServerApi from "../api/fetch_server_api"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
import { ReportSources } from "./ReportSources"

function renderReportSources(report, expandedItems, theDataModel) {
    const settings = createTestableSettings()
    if (expandedItems) {
        settings.expandedItems.value = expandedItems
    }
    return render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={theDataModel ?? dataModel}>
                <ReportSources reload={vi.fn()} report={report} settings={settings} />
            </DataModel.Provider>
            ,
        </Permissions.Provider>,
    )
}

beforeEach(() => vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true }))

it("shows a message if the report has no subjects", async () => {
    const { container } = renderReportSources({})
    expect(screen.getAllByText(/No sources have been configured yet/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows a message if none of the subjects has metrics", async () => {
    const { container } = renderReportSources({ subjects: { subject_uuid: {} } })
    expect(screen.getAllByText(/No sources have been configured yet/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows the sources", async () => {
    const { container } = renderReportSources(report)
    expect(screen.getAllByText(/Source 2/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows a message for sources without url", async () => {
    const { container } = renderReportSources(
        {
            subjects: {
                subject_uuid: {
                    metrics: {
                        metric_uuid: {
                            sources: {
                                source_uuid: { type: "source_type_without_location_parameters", parameters: {} },
                            },
                        },
                    },
                },
            },
        },
        ["source_uuid:0"],
    )
    expect(screen.getAllByText(/This source has no location parameters/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("counts the metrics", async () => {
    const { container } = renderReportSources(report)
    expect(screen.getAllByText("1").length).toBe(2) // Two sources, each used once
    await expectNoAccessibilityViolations(container)
})

it("counts the metrics using the same source", async () => {
    const { container } = renderReportSources({
        subjects: {
            subject_uuid: {
                metrics: {
                    metric_uuid1: {
                        sources: { source_uuid: { type: "source_type", parameters: { url: "https://source.org" } } },
                    },
                    metric_uuid2: {
                        sources: { source_uuid: { type: "source_type", parameters: { url: "https://source.org" } } },
                    },
                },
            },
        },
    })
    expect(screen.getAllByText("2").length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("considers sources different if only the API-version differs", async () => {
    const { container } = renderReportSources({
        subjects: {
            subject_uuid: {
                metrics: {
                    metric_uuid1: {
                        sources: {
                            source_uuid1: {
                                type: "source_type",
                                parameters: { url: "https://source.org", api_version: "v2" },
                            },
                        },
                    },
                    metric_uuid2: {
                        sources: {
                            source_uuid2: {
                                type: "source_type",
                                parameters: { url: "https://source.org", api_version: "v3" },
                            },
                        },
                    },
                },
            },
        },
    })
    expect(screen.getAllByText("1").length).toBe(2) // Two sources, each used once
    await expectNoAccessibilityViolations(container)
})

it("shows the default source name if the source doesn't have an own name", async () => {
    const { container } = renderReportSources({
        subjects: {
            subject_uuid: {
                metrics: {
                    metric_uuid: {
                        sources: { source_uuid: { type: "source_type", parameters: { url: "https://source.org" } } },
                    },
                },
            },
        },
    })
    expect(screen.getAllByText("Source type name").length).toBe(2) // Source type and source name are equal
    await expectNoAccessibilityViolations(container)
})

it("changes the value of a parameter of a source without parameter layout", async () => {
    const { container } = renderReportSources(
        {
            subjects: {
                subject_uuid: {
                    metrics: {
                        metric_uuid: {
                            sources: {
                                source_uuid: { type: "source_type", parameters: { url: "https://source.org" } },
                            },
                        },
                    },
                },
            },
        },
        ["source_uuid:0"],
    )
    await userEvent.type(screen.getByLabelText(/URL/), "/new{Enter}")
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith("post", "source/source_uuid/parameter/url", {
        url: "https://source.org/new",
        edit_scope: "report",
    })
    await expectNoAccessibilityViolations(container)
})

it("changes the value of a parameter of a source with parameter layout", async () => {
    const theDataModel = { ...dataModel }
    theDataModel.sources["source_type"].parameters = {
        api_version: { name: "API version", type: "string" },
    }
    theDataModel.sources["source_type"].parameter_layout = {
        location: { parameters: ["api_version"] },
    }
    const { container } = renderReportSources(
        {
            subjects: {
                subject_uuid: {
                    metrics: {
                        metric_uuid: {
                            sources: {
                                source_uuid: { type: "source_type", parameters: { api_version: "2" } },
                            },
                        },
                    },
                },
            },
        },
        ["source_uuid:0"],
        theDataModel,
    )
    await userEvent.type(screen.getByLabelText(/API version/), "{Backspace}3{Enter}")
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith("post", "source/source_uuid/parameter/api_version", {
        api_version: "3",
        edit_scope: "report",
    })
    await expectNoAccessibilityViolations(container)
})

function expectOrder(expected) {
    const rows = screen.getAllByText(/source1|source2/)
    for (let index = 0; index < expected.length; index++) {
        expect(rows[index]).toHaveTextContent(expected[index])
    }
}

function createReport(name1, name2) {
    return {
        subjects: {
            subject_uuid: {
                metrics: {
                    metric_uuid1: {
                        sources: {
                            source_uuid1: {
                                type: "source_type",
                                name: name1,
                                parameters: { url: "https://source1.org" },
                            },
                        },
                    },
                    metric_uuid2: {
                        sources: {
                            source_uuid2: {
                                type: "source_type",
                                name: name2,
                                parameters: { url: "https://source2.org" },
                            },
                        },
                    },
                },
            },
        },
    }
}

it("sorts the sources by name", async () => {
    const { container } = renderReportSources(createReport("source2", "source1"))
    expectOrder(["source1", "source2"])
    await expectNoAccessibilityViolations(container)
})

it("sorts the sources by type if not all names are available", async () => {
    const { container } = renderReportSources(createReport("", "source1"))
    expectOrder(["https://source1.org", "source1"]) // "Source type" comes before "source1"
    await expectNoAccessibilityViolations(container)
})

it("sorts the sources by type if no names are available", async () => {
    const { container } = renderReportSources(createReport("", ""))
    expectOrder(["https://source1.org", "https://source2.org"]) // Source order unchanged because the source types are equal
    await expectNoAccessibilityViolations(container)
})
