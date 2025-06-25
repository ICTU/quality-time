import { render, screen } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings, dataModel, report } from "../__fixtures__/fixtures"
import { DataModel } from "../context/DataModel"
import { expectNoAccessibilityViolations } from "../testUtils"
import { Subject } from "./Subject"

function renderSubject({
    atReportsOverview = false,
    dates = [new Date()],
    reportDate = null,
    reportToRender = null,
} = {}) {
    const settings = createTestableSettings()
    return render(
        <DataModel.Provider value={dataModel}>
            <Subject
                atReportsOverview={atReportsOverview}
                dates={dates}
                handleSort={() => vi.fn()}
                measurements={[]}
                report={reportToRender || report}
                reportDate={reportDate}
                settings={settings}
                subjectUuid="subject_uuid"
                tags={[]}
            />
        </DataModel.Provider>,
    )
}

beforeEach(() => {
    history.push("")
})

it("shows the subject title", async () => {
    const { container } = renderSubject({ dates: [new Date(2022, 3, 26)] })
    expect(screen.queryAllByText("Subject 1 title").length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows the subject title at the reports overview", async () => {
    const { container } = renderSubject({ atReportsOverview: true, dates: [new Date(2022, 3, 26)] })
    expect(screen.queryAllByText("Report title ❯ Subject 1 title").length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("hides metrics not requiring action", async () => {
    history.push("?metrics_to_hide=no_action_required")
    renderSubject()
    expect(screen.queryAllByText(/M\d/).length).toBe(1)
})

it("hides the subject if all metrics are hidden", async () => {
    history.push("?hidden_tags=tag,other tag")
    renderSubject()
    expect(screen.queryAllByText("Subject 1 title").length).toBe(0)
})

const reportWithEmptySubject = {
    reportToRender: {
        subjects: { subject_uuid: { name: "Subject 1 title", metrics: {}, type: "subject_type" } },
    },
}

it("does not hide an empty subject if no metrics are hidden", async () => {
    renderSubject(reportWithEmptySubject)
    expect(screen.queryAllByText("Subject 1 title").length).toBe(1)
})

it("hides an empty subject if metrics that require action are hidden", async () => {
    history.push("?metrics_to_hide=no_action_required")
    renderSubject(reportWithEmptySubject)
    expect(screen.queryAllByText("Subject 1 title").length).toBe(0)
})

it("hides an empty subject if metrics with tags are hidden", async () => {
    history.push("?hidden_tags=tag,other tag")
    renderSubject(reportWithEmptySubject)
    expect(screen.queryAllByText("Subject 1 title").length).toBe(0)
})

function expectOrder(metricNames) {
    expect(screen.getAllByText(/M\d/).map((element) => element.textContent.trim())).toStrictEqual(metricNames)
}

for (const attribute of [
    "name",
    "measurement",
    "target",
    "comment",
    "source",
    "issues",
    "tags",
    "unit",
    "status",
    "time_left",
    "overrun",
]) {
    for (const order of ["ascending", "descending"]) {
        it("sorts metrics by attribute", async () => {
            history.push(`?sort_column=${attribute}&sort_direction=${order}`)
            renderSubject()
            expectOrder(order === "ascending" ? ["M1", "M2"] : ["M2", "M1"])
        })
    }
}
