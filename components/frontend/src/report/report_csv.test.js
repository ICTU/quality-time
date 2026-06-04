import { listSeparator, reportToCSV } from "./report_csv"

const dataModel = {
    metrics: {
        violations: {
            name: "Violations",
            default_scale: "count",
            direction: "<",
            unit: "violations",
            unit_singular: "violation",
            sources: ["sonarqube"],
        },
    },
    sources: { sonarqube: { name: "SonarQube" } },
}

function makeReport() {
    return {
        report_uuid: "r1",
        subjects: {
            s1: {
                name: "Subject 1",
                type: "software",
                metrics: {
                    m1: {
                        type: "violations",
                        name: "M1",
                        status: "target_not_met",
                        target: "10",
                        latest_measurement: { count: { value: "20", status: "target_not_met" } },
                        sources: { src1: { type: "sonarqube", name: "Src" } },
                        tags: ["security"],
                        comment: "<b>bold</b> comment",
                        issue_ids: ["ISSUE-1"],
                    },
                    m2: {
                        type: "violations",
                        name: "M2",
                        status: "target_met",
                        target: "0",
                        latest_measurement: { count: { value: "0", status: "target_met" } },
                        sources: {},
                        tags: ["performance"],
                        comment: "",
                        issue_ids: [],
                    },
                },
            },
        },
    }
}

function makeSettings(overrides = {}) {
    const settings = {
        metricsToHide: { value: "none", isDefault: () => true },
        hiddenTags: { value: [], isDefault: () => true },
        sortColumn: { value: "" },
        sortDirection: { value: "ascending" },
        hiddenColumns: { value: [] },
        hideEmptyColumns: { value: false },
        dateOrder: { value: "ascending" },
    }
    return { ...settings, ...overrides }
}

function rows(csv) {
    return csv.split("\r\n")
}

it("exports a header and a row per visible metric", () => {
    const csv = reportToCSV(makeReport(), [], [new Date()], makeSettings(), dataModel)
    const lines = rows(csv)
    expect(lines[0]).toBe("Subject,Metric,Status,Measurement,Target,Unit,Sources,Time left,Comment,Issues,Tags")
    expect(lines[1]).toBe("Subject 1,M1,Target not met,20,≦ 10,violations,Src,,bold comment,ISSUE-1,security")
    expect(lines[2]).toBe("Subject 1,M2,Target met,0,≦ 0,violations,,,,,performance")
})

it("omits the overrun column in single-date view and the trend column always", () => {
    const csv = reportToCSV(makeReport(), [], [new Date()], makeSettings(), dataModel)
    expect(rows(csv)[0]).not.toContain("Overrun")
    expect(rows(csv)[0]).not.toContain("Trend")
})

it("honors explicitly hidden columns", () => {
    const settings = makeSettings({ hiddenColumns: { value: ["comment", "tags"] } })
    const csv = reportToCSV(makeReport(), [], [new Date()], settings, dataModel)
    expect(rows(csv)[0]).toBe("Subject,Metric,Status,Measurement,Target,Unit,Sources,Time left,Issues")
})

it("hides empty columns when requested", () => {
    const report = makeReport()
    // No metric has tags, so the tags column should disappear when hiding empty columns
    report.subjects.s1.metrics.m1.tags = []
    report.subjects.s1.metrics.m2.tags = []
    const settings = makeSettings({ hideEmptyColumns: { value: true } })
    const csv = reportToCSV(report, [], [new Date()], settings, dataModel)
    expect(rows(csv)[0]).not.toContain("Tags")
})

it("hides metrics filtered out by tag", () => {
    const settings = makeSettings({ hiddenTags: { value: ["performance"], isDefault: () => false } })
    const csv = reportToCSV(makeReport(), [], [new Date()], settings, dataModel)
    const lines = rows(csv)
    expect(lines).toHaveLength(2) // header + M1 only
    expect(lines[1]).toContain("M1")
})

it("sorts metrics like the table", () => {
    const settings = makeSettings({ sortColumn: { value: "name" }, sortDirection: { value: "descending" } })
    const csv = reportToCSV(makeReport(), [], [new Date()], settings, dataModel)
    const lines = rows(csv)
    expect(lines[1]).toContain("M2")
    expect(lines[2]).toContain("M1")
})

it("produces value and delta columns for a multi-date view", () => {
    const dates = [new Date("2024-01-01T12:00:00Z"), new Date("2024-01-08T12:00:00Z")]
    const measurements = [
        {
            metric_uuid: "m1",
            start: "2024-01-01T00:00:00+00:00",
            end: "2024-01-01T23:59:59+00:00",
            count: { value: "20", status: "target_not_met" },
        },
        {
            metric_uuid: "m1",
            start: "2024-01-08T00:00:00+00:00",
            end: "2024-01-08T23:59:59+00:00",
            count: { value: "15", status: "near_target_met" },
        },
    ]
    const csv = reportToCSV(makeReport(), measurements, dates, makeSettings(), dataModel)
    const lines = rows(csv)
    const expectedHeader = [
        "Subject",
        "Metric",
        dates[0].toLocaleDateString(),
        "𝚫",
        dates[1].toLocaleDateString(),
        "Unit",
        "Sources",
        "Time left",
        "Overrun",
        "Comment",
        "Issues",
        "Tags",
    ].join(",")
    expect(lines[0]).toBe(expectedHeader)
    // M1 has a measurement on both dates: value 20, delta -5, value 15
    expect(lines[1]).toContain("20,-5,15")
    // M2 has no measurements on these dates: ?, no delta, ?
    expect(lines[2]).toContain("?,,?")
})

it("escapes fields containing commas, quotes, and newlines", () => {
    const report = makeReport()
    report.subjects.s1.metrics.m1.comment = 'a, "b"\nc'
    const csv = reportToCSV(report, [], [new Date()], makeSettings(), dataModel)
    expect(csv).toContain('"a, ""b"" c"') // newline collapsed to space by htmlToText, comma/quotes escaped
})

it("neutralizes fields that a spreadsheet would interpret as a formula", () => {
    const report = makeReport()
    report.subjects.s1.metrics.m1.comment = "=1+2"
    report.subjects.s1.metrics.m2.comment = "-cmd" // starts with - but is not a number
    const csv = reportToCSV(report, [], [new Date()], makeSettings(), dataModel)
    expect(rows(csv)[1].split(",").at(-3)).toBe("'=1+2")
    expect(rows(csv)[2].split(",").at(-3)).toBe("'-cmd")
})

it("does not neutralize negative numbers", () => {
    // The delta value -5 in a multi-date view must remain a number, not be quoted as text
    const report = makeReport()
    report.subjects.s1.metrics = {
        m1: {
            type: "violations",
            name: "M1",
            status: "target_not_met",
            target: "10",
            latest_measurement: { count: { value: "20", status: "target_not_met" } },
            sources: {},
        },
    }
    const dates = [new Date("2024-01-01T12:00:00Z"), new Date("2024-01-08T12:00:00Z")]
    const measurements = [
        {
            metric_uuid: "m1",
            start: "2024-01-01T00:00:00+00:00",
            end: "2024-01-01T23:59:59+00:00",
            count: { value: "20", status: "target_not_met" },
        },
        {
            metric_uuid: "m1",
            start: "2024-01-08T00:00:00+00:00",
            end: "2024-01-08T23:59:59+00:00",
            count: { value: "15", status: "near_target_met" },
        },
    ]
    const csv = reportToCSV(report, measurements, dates, makeSettings(), dataModel)
    expect(rows(csv)[1]).toContain("20,-5,15")
})

it("uses the given delimiter and only quotes fields that contain it", () => {
    const report = makeReport()
    report.subjects.s1.metrics.m1.comment = "a, b" // contains a comma but not the semicolon delimiter
    report.subjects.s1.metrics.m2.comment = "x; y" // contains the semicolon delimiter
    const csv = reportToCSV(report, [], [new Date()], makeSettings(), dataModel, ";")
    expect(csv.split("\r\n")[0]).toContain("Subject;Metric;Status")
    expect(csv).toContain("a, b") // not quoted, the comma is not the delimiter
    expect(csv).toContain('"x; y"') // quoted, contains the delimiter
})

it("determines the list separator from the locale", () => {
    expect(listSeparator("en-US")).toBe(",")
    expect(listSeparator("en-GB")).toBe(",")
    expect(listSeparator("nl-NL")).toBe(";")
    expect(listSeparator("de-DE")).toBe(";")
})

it("strips HTML from comments but keeps link text and URL", () => {
    const report = makeReport()
    report.subjects.s1.metrics.m1.comment = "<a href='http://x'>link</a> and <em>emphasis</em>"
    const csv = reportToCSV(report, [], [new Date()], makeSettings(), dataModel)
    expect(rows(csv)[1]).toContain("link (http://x) and emphasis")
})

it("outputs only the URL when a link's text equals its URL", () => {
    const report = makeReport()
    report.subjects.s1.metrics.m1.comment = '<a href="http://x">http://x</a>'
    const csv = reportToCSV(report, [], [new Date()], makeSettings(), dataModel)
    const comment = rows(csv)[1].split(",").at(-3) // comment is the third-to-last column (before issues and tags)
    expect(comment).toBe("http://x")
})

it("keeps the text of a link without an href", () => {
    const report = makeReport()
    report.subjects.s1.metrics.m1.comment = "<a>just text</a>"
    const csv = reportToCSV(report, [], [new Date()], makeSettings(), dataModel)
    expect(rows(csv)[1]).toContain("just text")
})

it("outputs the URL of a link without link text", () => {
    const report = makeReport()
    report.subjects.s1.metrics.m1.comment = '<a href="http://x"></a>'
    const csv = reportToCSV(report, [], [new Date()], makeSettings(), dataModel)
    const comment = rows(csv)[1].split(",").at(-3)
    expect(comment).toBe("http://x")
})

it("includes the secondary name on a second line in the metric cell", () => {
    const report = makeReport()
    report.subjects.s1.metrics.m1.secondary_name = "secondary"
    const csv = reportToCSV(report, [], [new Date()], makeSettings(), dataModel)
    expect(csv).toContain('"M1\nsecondary"')
})

it("formats percentage measurements with a percent sign", () => {
    const report = makeReport()
    const metric = report.subjects.s1.metrics.m1
    metric.scale = "percentage"
    metric.latest_measurement = { percentage: { value: "42", status: "target_not_met" } }
    const csv = reportToCSV(report, [], [new Date()], makeSettings(), dataModel)
    expect(rows(csv)[1]).toContain("42%")
})

it("leaves the target empty when the metric does not evaluate targets", () => {
    const report = makeReport()
    report.subjects.s1.metrics.m1.evaluate_targets = false
    const csv = reportToCSV(report, [], [new Date()], makeSettings(), dataModel)
    // The target column is the fifth field; it should be empty for M1
    expect(rows(csv)[1].split(",")[4]).toBe("")
})

it("shows the time left for a metric with technical debt", () => {
    const report = makeReport()
    const metric = report.subjects.s1.metrics.m1
    metric.status = "debt_target_met"
    metric.debt_end_date = "3000-01-01"
    const csv = reportToCSV(report, [], [new Date()], makeSettings(), dataModel)
    expect(rows(csv)[1]).toMatch(/\d+ days/)
})

it("includes the identifying parameter values of a source on a second line", () => {
    const dataModelWithIdentifyingParameter = {
        ...dataModel,
        sources: { calendar: { name: "Calendar", identifying_parameters: ["branch"], parameters: { branch: {} } } },
    }
    const report = makeReport()
    report.subjects.s1.metrics.m1.sources = { src1: { type: "calendar", parameters: { branch: "main" } } }
    const csv = reportToCSV(report, [], [new Date()], makeSettings(), dataModelWithIdentifyingParameter)
    expect(csv).toContain('"Calendar\nmain"')
})

it("handles metrics without a measurement or sources", () => {
    const report = makeReport()
    report.subjects.s1.metrics.m1 = { type: "violations", name: "M1", status: "unknown", target: "10" }
    const csv = reportToCSV(report, [], [new Date()], makeSettings(), dataModel)
    const fields = rows(csv)[1].split(",")
    expect(fields[3]).toBe("?") // measurement
    expect(fields[6]).toBe("") // sources
})

it("shows the overrun for a metric that exceeded its desired reaction time", () => {
    const report = {
        report_uuid: "r1",
        subjects: {
            s1: {
                name: "Subject 1",
                metrics: {
                    m1: {
                        type: "violations",
                        name: "M1",
                        status: "target_not_met",
                        target: "10",
                        latest_measurement: { count: { value: "20", status: "target_not_met" } },
                        sources: {},
                    },
                },
            },
        },
    }
    const dates = [new Date("2024-01-01T12:00:00Z"), new Date("2024-06-01T12:00:00Z")]
    const measurements = [
        {
            metric_uuid: "m1",
            start: "2020-01-01T00:00:00+00:00",
            end: "2024-12-31T23:59:59+00:00",
            count: { value: "20", status: "target_not_met" },
        },
    ]
    const csv = reportToCSV(report, measurements, dates, makeSettings(), dataModel)
    expect(rows(csv)[1]).toMatch(/\d+ days/) // the overrun column
})

it("sorts measurements in reverse so the most recent measurement of a day is used", () => {
    const report = makeReport()
    report.subjects.s1.metrics = {
        m1: {
            type: "violations",
            name: "M1",
            status: "target_not_met",
            target: "10",
            latest_measurement: { count: { value: "20", status: "target_not_met" } },
            sources: {},
        },
    }
    const dates = [new Date("2024-01-01T12:00:00Z"), new Date("2024-01-08T12:00:00Z")]
    // Multiple, unordered measurements (two on the first day) exercise both branches of the reverse sort
    const measurements = [
        {
            metric_uuid: "m1",
            start: "2024-01-01T08:00:00+00:00",
            end: "2024-01-01T09:00:00+00:00",
            count: { value: "10", status: "target_not_met" },
        },
        {
            metric_uuid: "m1",
            start: "2024-01-08T00:00:00+00:00",
            end: "2024-01-08T23:59:59+00:00",
            count: { value: "15", status: "near_target_met" },
        },
        {
            metric_uuid: "m1",
            start: "2024-01-01T20:00:00+00:00",
            end: "2024-01-01T23:59:59+00:00",
            count: { value: "12", status: "target_not_met" },
        },
    ]
    const csv = reportToCSV(report, measurements, dates, makeSettings(), dataModel)
    // The most recent measurement on 2024-01-01 (value 12) is used, not the earlier one (value 10)
    expect(rows(csv)[1]).toContain("12,")
})

it("returns only a header for a report without subjects", () => {
    const csv = reportToCSV({ report_uuid: "r1" }, [], [new Date()], makeSettings(), dataModel)
    expect(csv).toBe("Subject,Metric")
})

it("returns only a header when all metrics are hidden", () => {
    const settings = makeSettings({ metricsToHide: { value: "all", isDefault: () => false } })
    const csv = reportToCSV(makeReport(), [], [new Date()], settings, dataModel)
    expect(rows(csv)).toHaveLength(1)
})
