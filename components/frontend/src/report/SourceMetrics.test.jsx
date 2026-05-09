import { render } from "@testing-library/react"

import { dataModel, report } from "../__fixtures__/fixtures"
import { DataModelContext } from "../context/DataModel"
import { expectText } from "../testUtils"
import { SourceMetrics } from "./SourceMetrics"

function renderSourceMetrics(theReport, source) {
    return render(
        <DataModelContext value={dataModel}>
            <SourceMetrics report={theReport} source={source} />
        </DataModelContext>,
    )
}

it("shows the metrics using the source", async () => {
    renderSourceMetrics(report, { name: "Source", type: "source_type", parameters: { url: "https://source1.org" } })
    expectText("M1")
})

it("shows the secondary names of metrics using the source", async () => {
    report.subjects["subject_uuid"].metrics["metric_uuid2"].secondary_name = "secondary name"
    renderSourceMetrics(report, { name: "Source 2", type: "source_type", parameters: { url: "https://source2.org" } })
    expectText(/M2.*secondary name/)
})
