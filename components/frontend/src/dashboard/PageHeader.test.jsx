import { render, renderHook, screen } from "@testing-library/react"
import { vi } from "vitest"

import { formatDate } from "../datetime"
import { expectNoAccessibilityViolations, expectText } from "../testUtils"
import { mockGetAnimations } from "./MockAnimations"
import { PageHeader } from "./PageHeader"

beforeEach(() => mockGetAnimations())

afterEach(() => vi.restoreAllMocks())

const mockLastUpdate = new Date("2024-03-26T12:34:56")

const report = {
    report_uuid: "report_uuid",
    title: "Title",
    subjects: {
        subject_uuid: {
            type: "subject_type",
            name: "Subject title",
            metrics: {
                metric_uuid: { name: "Metric name", type: "metric_type", tags: ["tag"], recent_measurements: [] },
                another_metric_uuid: {
                    name: "Metric name",
                    type: "metric_type",
                    tags: ["other"],
                    recent_measurements: [],
                },
            },
        },
    },
}

function renderPageHeader({ lastUpdate = new Date(), report = null, reportDate = null } = {}) {
    return render(<PageHeader lastUpdate={lastUpdate} report={report} reportDate={reportDate} />)
}

it("displays correct title for the reports overview", async () => {
    const { container } = renderPageHeader({})
    expectText(/Reports overview/)
    await expectNoAccessibilityViolations(container)
})

it("displays correct title for a report", async () => {
    const { container } = renderPageHeader({ report: report })
    expectText(/Title/)
    await expectNoAccessibilityViolations(container)
})

it("displays dates in en-GB format", async () => {
    const mockReportDate = new Date("2024-03-24T12:34:56")
    const { container } = renderPageHeader({ lastUpdate: mockLastUpdate, report: report, reportDate: mockReportDate })
    expectText(/Report date: 24\/03\/2024/)
    expectText(/Generated: 26\/03\/2024, 12:34/)
    await expectNoAccessibilityViolations(container)
})

it("displays report URL", async () => {
    const { container } = renderPageHeader({ report: report })
    expect(screen.getByTestId("reportUrl")).toBeInTheDocument()
    await expectNoAccessibilityViolations(container)
})

it("displays version link", async () => {
    const { container } = renderPageHeader({ lastUpdate: mockLastUpdate, report: report })
    expect(screen.getByTestId("version")).toBeInTheDocument()
    await expectNoAccessibilityViolations(container)
})

it("displays today as report date if no report date is provided", async () => {
    const { container } = renderPageHeader({ lastUpdate: mockLastUpdate, report: report })
    const expectedDate = renderHook(() => formatDate(new Date()))
    expectText(`Report date: ${expectedDate.result.current}`)
    await expectNoAccessibilityViolations(container)
})
