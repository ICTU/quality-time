import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings, dataModel, report } from "../__fixtures__/fixtures"
import * as fetchServerApi from "../api/fetch_server_api"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectFetch, expectNoAccessibilityViolations, expectNoText, expectText } from "../testUtils"
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
        </Permissions.Provider>,
    )
}

beforeEach(() => vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true }))

it("has no accessibility violations", async () => {
    const { container } = renderReportSources({})
    await expectNoAccessibilityViolations(container)
})

it("shows a message if the report has no subjects", async () => {
    renderReportSources({})
    expectText(/No sources have been configured yet/)
})

it("shows a message if none of the subjects has metrics", async () => {
    renderReportSources({ subjects: { subject_uuid: {} } })
    expectText(/No sources have been configured yet/)
})

it("shows the sources", async () => {
    renderReportSources(report)
    expectText(/Source 2/)
})

it("shows a message for sources without url", async () => {
    renderReportSources(
        {
            subjects: {
                subject_uuid: {
                    metrics: {
                        metric_uuid: {
                            type: "metric_type",
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
    expectText(/This source has no location parameters/)
})

it("counts the metrics", async () => {
    renderReportSources(report)
    expectText("1", 2) // Two sources, each used once and each without unused metric types
})

it("counts the metrics using the same source", async () => {
    renderReportSources({
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
    expectText("2")
})

it("considers sources different if only the API-version differs", async () => {
    renderReportSources({
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
    expectText("https://source.org", 2) // Two sources, each used once
})

it("shows the default source name if the source doesn't have an own name", async () => {
    renderReportSources({
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
    expectText("Source type name", 2) // Source type and source name are equal
})

it("considers a source without name the same as a source that has a name equal to the default name", async () => {
    renderReportSources({
        subjects: {
            subject_uuid: {
                metrics: {
                    metric_uuid1: {
                        sources: {
                            source_uuid1: { type: "source_type", parameters: { url: "https://sonarqube.org" } },
                        },
                    },
                    metric_uuid2: {
                        sources: {
                            source_uuid2: {
                                type: "source_type",
                                name: "Source type name",
                                parameters: { url: "https://sonarqube.org" },
                            },
                        },
                    },
                },
            },
        },
    })
    expectText("Source type name", 2) // Source type and source name are equal
})

it("changes the value of a parameter of a source without parameter layout", async () => {
    renderReportSources(
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
    await userEvent.type(screen.getAllByLabelText(/URL/)[0], "/new{Enter}")
    expectFetch("post", "source/source_uuid/parameter/url", { url: "https://source.org/new", edit_scope: "report" })
})

it("changes the value of a parameter of a source with parameter layout", async () => {
    const theDataModel = { ...dataModel }
    theDataModel.sources["source_type"].parameters = {
        api_version: { name: "API version", type: "string" },
    }
    theDataModel.sources["source_type"].parameter_layout = {
        location: { parameters: ["api_version"] },
    }
    renderReportSources(
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
    expectFetch("post", "source/source_uuid/parameter/api_version", { api_version: "3", edit_scope: "report" })
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
                        type: "metric_type",
                        sources: {
                            source_uuid1: {
                                type: "source_type",
                                name: name1,
                                parameters: { url: "https://source1.org" },
                            },
                        },
                    },
                    metric_uuid2: {
                        type: "metric_type",
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
    renderReportSources(createReport("source2", "source1"))
    expectOrder(["source1", "source2"])
})

it("sorts the sources by type if not all names are available", async () => {
    renderReportSources(createReport("", "source1"))
    expectOrder(["https://source1.org", "source1"]) // "Source type" comes before "source1"
})

it("sorts the sources by type if no names are available", async () => {
    renderReportSources(createReport("", ""))
    expectOrder(["https://source1.org", "https://source2.org"]) // Source order unchanged because the source types are equal
})

it("shows the metrics using the source", async () => {
    history.push("?expanded=source_uuid:1")
    renderReportSources(report)
    expectText("M1")
})

it("shows the secondary names of metrics using the source", async () => {
    history.push("?expanded=source_uuid2:1") // Use the second metric and source for better test coverage
    report.subjects["subject_uuid"].metrics["metric_uuid2"].secondary_name = "secondary name"
    renderReportSources(report)
    expectText(/M2.*secondary name/)
})

it("ignores an empty report", async () => {
    history.push("?expanded=source_uuid:1")
    renderReportSources({})
    expectText("No sources")
})

it("ignores subjects without metrics", async () => {
    history.push("?expanded=source_uuid:1")
    renderReportSources({ subjects: { subject_uuid: {} } })
    expectNoText("M1")
})

it("ignores metrics without sources", async () => {
    history.push("?expanded=source_uuid:1")
    renderReportSources({ subjects: { subject_uuid: { metrics: { metric_uuid: {} } } } })
    expectNoText("M1")
})

it("shows the unused metric types", async () => {
    history.push("?expanded=source_uuid2:2")
    const report = {
        subjects: {
            subject_uuid: {
                metrics: {
                    metric_uuid: {
                        type: "metric_type",
                        sources: {
                            source_uuid: {
                                type: "source_type",
                                parameters: { url: "https://example.org" },
                            },
                        },
                    },
                    metric_uuid2: {
                        type: "metric_type",
                        sources: {
                            source_uuid2: {
                                type: "source_type_without_location_parameters",
                                parameters: { url: "https://example.org" },
                            },
                        },
                    },
                },
            },
        },
    }
    renderReportSources(report)
    expectText("Metric type 2")
    const readTheDocsLink = screen.getByRole("link", { name: "Metric type 2" })
    expect(readTheDocsLink).toHaveAttribute("href", expect.stringContaining("#metric-type-2"))
    expectText("Metric type description")
    expectText("Metric type rationale")
})

it("shows a message if there are no unused metric types", async () => {
    history.push("?expanded=source_uuid:2")
    const report = {
        subjects: {
            subject_uuid: {
                metrics: {
                    metric_uuid: {
                        type: "metric_type",
                        sources: {
                            source_uuid: {
                                type: "source_type",
                                parameters: { url: "https://example.org" },
                            },
                        },
                    },
                },
            },
        },
    }
    renderReportSources(report)
    expectText("All metric types that this source supports are being used.")
})
