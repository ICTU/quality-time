import { render, screen } from "@testing-library/react";
import history from 'history/browser';
import { Subject } from "./Subject";
import { DataModel } from "../context/DataModel";
import { createTestableSettings, datamodel, report } from "../__fixtures__/fixtures";

function renderSubject(
    {
        atReportsOverview = false,
        dates = [new Date()],
        reportDate = null,
    } = {}
) {
    const settings = createTestableSettings()
    render(
        <DataModel.Provider value={datamodel}>
            <Subject
                atReportsOverview={atReportsOverview}
                dates={dates}
                handleSort={() => jest.fn()}
                measurements={[]}
                report={report}
                report_date={reportDate}
                settings={settings}
                subject_uuid="subject_uuid"
                tags={[]}
            />
        </DataModel.Provider>
    )
}

beforeEach(() => {
    history.push("")
})

it('shows the subject title', async () => {
    renderSubject({ dates: [new Date(2022, 3, 26)] })
    expect(screen.queryAllByText("Subject 1 title").length).toBe(1);
})

it('shows the subject title at the reports overview', async () => {
    renderSubject({ atReportsOverview: true, dates: [new Date(2022, 3, 26)] })
    expect(screen.queryAllByText("Report title ❯ Subject 1 title").length).toBe(1);
})

it('hides metrics not requiring action', async () => {
    history.push("?metrics_to_hide=no_action_needed")
    renderSubject()
    expect(screen.queryAllByText(/M\d/).length).toBe(1);
})

it('hides the subject if all metrics are hidden', async () => {
    history.push("?hidden_tags=tag,other tag")
    renderSubject();
    expect(screen.queryAllByText("Subject 1 title").length).toBe(0);
})

function expectOrder(metricNames) {
    expect(screen.getAllByText(/M\d/).map((element) => element.innerHTML)).toStrictEqual(metricNames)
}

for (const attribute of ["name", "measurement", "target", "comment", "source", "issues", "tags", "unit", "status", "time_left", "overrun"]) {
    for (const order of ["ascending", "descending"]) {
        it('sorts metrics by attribute', async () => {
            history.push(`?sort_column=${attribute}&sort_direction=${order}`)
            renderSubject();
            expectOrder(order === "ascending" ? ["M1", "M2"] : ["M2", "M1"])
        })
    }
}
