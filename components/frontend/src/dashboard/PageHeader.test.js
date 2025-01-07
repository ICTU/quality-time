import { render, screen } from "@testing-library/react"

import { mockGetAnimations } from "./MockAnimations"
import { PageHeader } from "./PageHeader"

beforeEach(() => mockGetAnimations())

afterEach(() => jest.restoreAllMocks())

const mockReportDate = new Date("2024-03-24T12:34:56")
const mockLastUpdate = new Date("2024-03-26T12:34:56")
const mockDateOfToday = new Date()
    .toLocaleDateString("en-GB", { year: "numeric", month: "2-digit", day: "2-digit" })
    .replace(/\//g, "-")

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
    render(<PageHeader lastUpdate={lastUpdate} report={report} reportDate={reportDate} />)
}

it("displays correct title for the reports overview", () => {
    renderPageHeader({})
    expect(screen.getByText(/Reports overview/)).toBeInTheDocument()
})

it("displays correct title for a report", () => {
    renderPageHeader({ report: report })
    expect(screen.getByText(/Title/)).toBeInTheDocument()
})

it("displays dates in en-GB format", () => {
    renderPageHeader({ lastUpdate: mockLastUpdate, report: report, reportDate: mockReportDate })
    expect(screen.getByText(/Report date: 24-03-2024/)).toBeInTheDocument()
    expect(screen.getByText(/Generated: 26-03-2024, 12:34/)).toBeInTheDocument()
})

it("displays report URL", () => {
    renderPageHeader({ report: report })
    expect(screen.getByTestId("reportUrl")).toBeInTheDocument()
})

it("displays version link", () => {
    renderPageHeader({ lastUpdate: mockLastUpdate, report: report })
    expect(screen.getByTestId("version")).toBeInTheDocument()
})

it("displays today as report date if no report date is provided", () => {
    renderPageHeader({ lastUpdate: mockLastUpdate, report: report })
    expect(screen.getByText(`Report date: ${mockDateOfToday}`)).toBeInTheDocument()
})
