import { render, screen } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { dataModel, report } from "../__fixtures__/fixtures"
import * as fetchServerApi from "../api/fetch_server_api"
import { useSettings } from "../app_ui_settings"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import {
    asyncClickLabeledElement,
    expectNoAccessibilityViolations,
    expectNoText,
    expectSearch,
    expectText,
} from "../testUtils"
import { SnackbarAlerts } from "../widgets/SnackbarAlerts"
import { ReportSources } from "./ReportSources"

function ReportSourcesWrapper({ report, showMessage, theDataModel }) {
    const settings = useSettings()
    return (
        <PermissionsContext value={[EDIT_REPORT_PERMISSION]}>
            <DataModelContext value={theDataModel ?? dataModel}>
                <SnackbarAlerts messages={[]} showMessage={showMessage ?? vi.fn()}>
                    <ReportSources reload={vi.fn()} report={report} settings={settings} />
                </SnackbarAlerts>
            </DataModelContext>
        </PermissionsContext>
    )
}

function renderReportSources(report, showMessage, theDataModel) {
    return render(<ReportSourcesWrapper report={report} showMessage={showMessage} theDataModel={theDataModel} />)
}

beforeEach(() => {
    history.push("")
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true })
})

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

it("shows sources without url", async () => {
    renderReportSources({
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
    })
    expectText("Source type without location parameters", 2) // Source name (defaulted) and source type
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

it("toggles a source's expanded state when its row is expanded", async () => {
    renderReportSources(report)
    await asyncClickLabeledElement(/Expand/, 0)
    expectSearch("?expanded=source_uuid%3A0")
})
