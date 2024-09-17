import { EDIT_ENTITY_PERMISSION, EDIT_REPORT_PERMISSION } from "./context/Permissions"
import { defaultDesiredResponseTimes } from "./defaults"
import {
    addCounts,
    capitalize,
    getMetricResponseDeadline,
    getMetricResponseOverrun,
    getMetricTags,
    getMetricTarget,
    getReportTags,
    getSourceName,
    getSubjectName,
    getSubjectType,
    getSubjectTypeMetrics,
    getUserPermissions,
    isMeasurementRequested,
    niceNumber,
    nrMetricsInReport,
    nrMetricsInReports,
    scaledNumber,
    sortWithLocaleCompare,
    sum,
    userPrefersDarkMode,
    visibleMetrics,
} from "./utils"

const dataModel = {
    metrics: {
        metric_type: {
            default_scale: "count",
        },
    },
}

const metric = {
    type: "metric_type",
}

it("capitalizes strings", () => {
    expect(capitalize("")).toBe("")
    expect(capitalize("A")).toBe("A")
    expect(capitalize("a")).toBe("A")
    expect(capitalize("ab")).toBe("Ab")
    expect(capitalize("aB")).toBe("AB")
    expect(capitalize("AB")).toBe("AB")
    expect(capitalize("a_b")).toBe("A b")
})

it("rounds numbers nicely", () => {
    expect(niceNumber(0)).toBe(10)
    expect(niceNumber(1)).toBe(10)
    expect(niceNumber(9)).toBe(10)
    expect(niceNumber(10)).toBe(12)
    expect(niceNumber(12)).toBe(15)
    expect(niceNumber(15)).toBe(20)
    expect(niceNumber(16)).toBe(20)
    expect(niceNumber(17)).toBe(20)
    expect(niceNumber(39)).toBe(50)
    expect(niceNumber(40)).toBe(50)
    expect(niceNumber(41)).toBe(50)
    expect(niceNumber(79)).toBe(100)
    expect(niceNumber(80)).toBe(100)
    expect(niceNumber(81)).toBe(100)
    expect(niceNumber(90)).toBe(100)
    expect(niceNumber(100)).toBe(120)
    expect(niceNumber(125)).toBe(150)
})

it("adds a scale", () => {
    expect(scaledNumber(1)).toBe("1")
    expect(scaledNumber(12)).toBe("12")
    expect(scaledNumber(123)).toBe("123")
    expect(scaledNumber(1234)).toBe("1k")
    expect(scaledNumber(12345)).toBe("12k")
    expect(scaledNumber(123456)).toBe("123k")
    expect(scaledNumber(1234567)).toBe("1m")
    expect(scaledNumber(12345678)).toBe("12m")
    expect(scaledNumber(123456789)).toBe("123m")
})

it("gives users all permissions if permissions have not been limited", () => {
    const permissions = getUserPermissions("jodoe", "john.doe@example.org", null, {})
    expect(permissions).toStrictEqual([EDIT_REPORT_PERMISSION, EDIT_ENTITY_PERMISSION])
})

it("gives users edit report permissions if edit report permissions have been granted", () => {
    const permissions = getUserPermissions("jodoe", "john.doe@example.org", null, {
        [EDIT_REPORT_PERMISSION]: ["jodoe"],
        [EDIT_ENTITY_PERMISSION]: ["jadoe"],
    })
    expect(permissions).toStrictEqual([EDIT_REPORT_PERMISSION])
})

it("gives users edit entity permissions if edit entity permissions have been granted", () => {
    const permissions = getUserPermissions("jodoe", "john.doe@example.org", null, {
        [EDIT_REPORT_PERMISSION]: ["jadoe"],
        [EDIT_ENTITY_PERMISSION]: ["jodoe"],
    })
    expect(permissions).toStrictEqual([EDIT_ENTITY_PERMISSION])
})

it("gives users no permissions if they have not logged in", () => {
    const permissions = getUserPermissions(null, null, null, {})
    expect(permissions).toStrictEqual([])
})

it("gives users no permissions if the report date is in the past", () => {
    const permissions = getUserPermissions("jodoe", "john.doe@example.org", new Date(), {})
    expect(permissions).toStrictEqual([])
})

it("gets the metric tags sorted", () => {
    expect(getMetricTags({ tags: ["foo", "bar"] })).toStrictEqual(["bar", "foo"])
})

it("gets the metric tags even if there are none", () => {
    expect(getMetricTags({})).toStrictEqual([])
})

it("gets the metric target", () => {
    expect(getMetricTarget({ target: "2" })).toStrictEqual("2")
})

it("gets the metric target, even if the target is missing", () => {
    expect(getMetricTarget({})).toStrictEqual("0")
})

it("gets the source name", () => {
    expect(getSourceName({ name: "source" }, {})).toStrictEqual("source")
})

it("gets the source name from the data model if the source has no name", () => {
    expect(getSourceName({ type: "source_type" }, { sources: { source_type: { name: "source" } } })).toStrictEqual(
        "source",
    )
})

it("gets the subject type", () => {
    const subject = { name: "Subject" }
    expect(getSubjectType("subject", { subject: subject })).toStrictEqual({ name: "Subject" })
})

it("gets the subject type recursively", () => {
    const subject = { name: "Subject" }
    expect(getSubjectType("subject", { parent: { subjects: { subject: subject } } })).toStrictEqual({
        name: "Subject",
    })
})

it("gets the subject type recursively from the second subject type", () => {
    const subject = { name: "Subject" }
    expect(
        getSubjectType("subject", {
            first: { subjects: { foo: { name: "Foo" } } },
            second: { subjects: { subject: subject } },
        }),
    ).toStrictEqual(subject)
})

it("gets the subject type metrics", () => {
    expect(getSubjectTypeMetrics("subject", { subject: { metrics: ["metric"] } })).toStrictEqual(["metric"])
})

it("gets the subject type metrics recursively", () => {
    const metrics = getSubjectTypeMetrics("child", {
        parent: { metrics: ["parent metric"], subjects: { child: { metrics: ["child metric"] } } },
    })
    expect(metrics).toStrictEqual(["child metric"])
})

it("gets the subject type metrics recursively, including child metrics", () => {
    const metrics = getSubjectTypeMetrics("parent", {
        parent: { metrics: ["parent metric"], subjects: { child: { metrics: ["child metric"] } } },
    })
    expect(metrics).toStrictEqual(["parent metric", "child metric"])
})

it("gets the subject type metrics recursively from the second subject type", () => {
    const metrics = getSubjectTypeMetrics("child", {
        first: { subjects: { foo: { metrics: ["foo metric"] } } },
        second: { metrics: ["second metric"], subjects: { child: { metrics: ["child metric"] } } },
    })
    expect(metrics).toStrictEqual(["child metric"])
})

it("gets the subject type metrics deduplicated", () => {
    const metrics = getSubjectTypeMetrics("parent", {
        parent: { subjects: { child1: { metrics: ["child metric"] }, child2: { metrics: ["child metric"] } } },
    })
    expect(metrics).toStrictEqual(["child metric"])
})

it("gets the subject name", () => {
    expect(getSubjectName({ name: "subject" }, {})).toStrictEqual("subject")
})

it("gets the subject name from the data model if the subject has no name", () => {
    expect(getSubjectName({ type: "subject_type" }, { subjects: { subject_type: { name: "subject" } } })).toStrictEqual(
        "subject",
    )
})

it("returns true when the user sets dark mode", () => {
    expect(userPrefersDarkMode("dark")).toBe(true)
})

it("returns false when the user sets light mode", () => {
    expect(userPrefersDarkMode("light")).toBe(false)
})

function mockMatchMedia(matches, addEventListener) {
    Object.defineProperty(window, "matchMedia", {
        value: jest.fn().mockImplementation((_query) => ({
            matches: matches ?? false,
            addEventListener: addEventListener ?? jest.fn(),
            removeEventListener: jest.fn(),
            addListener: jest.fn(), // deprecated
            removeListener: jest.fn(), // deprecated
        })),
        configurable: true,
    })
}

it("returns true when the user prefers dark mode", () => {
    mockMatchMedia(true)
    expect(userPrefersDarkMode("system")).toBe(true)
})

it("returns false when the user prefers light mode", () => {
    mockMatchMedia(false)
    expect(userPrefersDarkMode("system")).toBe(false)
})

it("returns the metric response deadline", () => {
    expect(getMetricResponseDeadline({}, {})).toStrictEqual(null)
})

it("returns the metric response deadline based on the tech debt end date", () => {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    expect(
        getMetricResponseDeadline({ status: "debt_target_met", debt_end_date: tomorrow.toISOString() }, {}),
    ).toStrictEqual(tomorrow)
})

it("returns the metric response deadline based on the desired response time", () => {
    const statusStart = "2024-01-01"
    const expectedDeadline = new Date(statusStart)
    expectedDeadline.setDate(expectedDeadline.getDate() + defaultDesiredResponseTimes.near_target_met)
    expect(getMetricResponseDeadline({ status: "near_target_met", status_start: statusStart }, {})).toStrictEqual(
        expectedDeadline,
    )
})

it("does not return a metric response deadline when the report has been configured not to have a desired response time", () => {
    const report = { desired_response_times: { near_target_met: "" } }
    expect(getMetricResponseDeadline({ status: "near_target_met", status_start: "2024-02-02" }, report)).toStrictEqual(
        null,
    )
})

it("returns the metric response overrun when there are no measurements", () => {
    expect(getMetricResponseOverrun("uuid", metric, {}, [], dataModel)).toStrictEqual({
        overruns: [],
        totalOverrun: 0,
    })
})

it("returns the metric response overrun when there is no overrun", () => {
    const measurements = [{ metric_uuid: "uuid", start: "2000-01-01", end: "2000-01-04" }]
    expect(getMetricResponseOverrun("uuid", metric, {}, measurements, dataModel)).toStrictEqual({
        overruns: [],
        totalOverrun: 0,
    })
})

it("returns the metric response overrun when there is one long measurement", () => {
    const measurements = [{ metric_uuid: "uuid", start: "2000-01-01", end: "2000-01-31" }]
    expect(getMetricResponseOverrun("uuid", metric, {}, measurements, dataModel)).toStrictEqual({
        overruns: [
            {
                status: "unknown",
                start: "2000-01-01",
                end: "2000-01-31",
                actual_response_time: 30,
                desired_response_time: 3,
                overrun: 27,
            },
        ],
        totalOverrun: 27,
    })
})

it("returns the metric response overrun when there is one long measurement and the report has no desired response times", () => {
    const report = { desired_response_times: { unknown: "" } }
    const measurements = [{ metric_uuid: "uuid", start: "2000-01-01", end: "2000-01-31" }]
    expect(getMetricResponseOverrun("uuid", metric, report, measurements, dataModel)).toStrictEqual({
        overruns: [],
        totalOverrun: 0,
    })
})

it("returns the metric response overrun when there is one long measurement and the report has desired response times", () => {
    const report = { desired_response_times: { unknown: "10" } }
    const measurements = [{ metric_uuid: "uuid", start: "2000-01-01", end: "2000-01-31" }]
    expect(getMetricResponseOverrun("uuid", metric, report, measurements, dataModel)).toStrictEqual({
        overruns: [
            {
                status: "unknown",
                start: "2000-01-01",
                end: "2000-01-31",
                actual_response_time: 30,
                desired_response_time: 10,
                overrun: 20,
            },
        ],
        totalOverrun: 20,
    })
})

it("returns the metric response overrun when the metric status is target met", () => {
    const measurements = [
        {
            metric_uuid: "uuid",
            start: "2000-01-01",
            end: "2000-01-31",
            count: { status: "target_met" },
        },
    ]
    expect(getMetricResponseOverrun("uuid", metric, {}, measurements, dataModel)).toStrictEqual({
        overruns: [],
        totalOverrun: 0,
    })
})

it("returns the metric response overrun when the metric status is target not met", () => {
    const measurements = [
        {
            metric_uuid: "uuid",
            start: "2000-01-01",
            end: "2000-01-31",
            count: { status: "target_not_met" },
        },
    ]
    expect(getMetricResponseOverrun("uuid", metric, {}, measurements, dataModel)).toStrictEqual({
        overruns: [
            {
                status: "target_not_met",
                start: "2000-01-01",
                end: "2000-01-31",
                actual_response_time: 30,
                desired_response_time: 7,
                overrun: 23,
            },
        ],
        totalOverrun: 23,
    })
})

it("returns the metric response overrun when there are two consecutive measurements that together overrun", () => {
    const measurements = [
        { metric_uuid: "uuid", start: "2000-01-01", end: "2000-01-03" },
        { metric_uuid: "uuid", start: "2000-01-03", end: "2000-01-05" },
    ]
    expect(getMetricResponseOverrun("uuid", metric, {}, measurements, dataModel)).toStrictEqual({
        overruns: [
            {
                status: "unknown",
                start: "2000-01-01",
                end: "2000-01-05",
                actual_response_time: 4,
                desired_response_time: 3,
                overrun: 1,
            },
        ],
        totalOverrun: 1,
    })
})

it("returns the metric response overrun when there are two measurements with different statuses", () => {
    const measurements = [
        { metric_uuid: "uuid", start: "2000-01-01", end: "2000-01-03" },
        {
            metric_uuid: "uuid",
            start: "2000-01-03",
            end: "2000-01-05",
            count: { status: "target_met" },
        },
    ]
    expect(getMetricResponseOverrun("uuid", metric, {}, measurements, dataModel)).toStrictEqual({
        overruns: [],
        totalOverrun: 0,
    })
})

it("returns the tags of an empty report", () => {
    expect(getReportTags({ subjects: {} })).toStrictEqual([])
})

it("returns the tags of a report with one tag", () => {
    expect(
        getReportTags({
            subjects: { subject_uud: { metrics: { metric_uuid: { tags: ["tag"] } } } },
        }),
    ).toStrictEqual(["tag"])
})

it("does not return hidden tags", () => {
    expect(
        getReportTags(
            {
                subjects: {
                    subject_uud: { metrics: { metric_uuid: { tags: ["tag", "hidden"] } } },
                },
            },
            ["hidden"],
        ),
    ).toStrictEqual(["tag"])
})

it("hides metrics not requiring action or without issues", () => {
    expect(visibleMetrics({}, "no_action_required", [])).toStrictEqual({})
    expect(visibleMetrics({}, "no_issues", [])).toStrictEqual({})
    expect(visibleMetrics({}, "all", [])).toStrictEqual({})
    expect(visibleMetrics({}, "none", [])).toStrictEqual({})
    const metricNotRequiringAction = { metric_uuid: { status: "informative" } }
    expect(visibleMetrics(metricNotRequiringAction, "no_action_required", [])).toStrictEqual({})
    expect(visibleMetrics(metricNotRequiringAction, "no_issues", [])).toStrictEqual({})
    expect(visibleMetrics(metricNotRequiringAction, "all", [])).toStrictEqual({})
    expect(visibleMetrics(metricNotRequiringAction, "none", [])).toStrictEqual(metricNotRequiringAction)
    const metricRequiringAction = { metric_uuid: { status: "target_not_met" } }
    expect(visibleMetrics(metricRequiringAction, "no_action_required", [])).toStrictEqual(metricRequiringAction)
    expect(visibleMetrics(metricRequiringAction, "no_issues", [])).toStrictEqual({})
    expect(visibleMetrics(metricRequiringAction, "none", [])).toStrictEqual(metricRequiringAction)
    expect(visibleMetrics(metricRequiringAction, "all", [])).toStrictEqual({})
    const metricWithIssue = { metric_uuid: { status: "target_met", issue_ids: ["ID-1"] } }
    expect(visibleMetrics(metricWithIssue, "no_action_required", [])).toStrictEqual({})
    expect(visibleMetrics(metricWithIssue, "no_issues", [])).toStrictEqual(metricWithIssue)
    expect(visibleMetrics(metricWithIssue, "none", [])).toStrictEqual(metricWithIssue)
    expect(visibleMetrics(metricWithIssue, "all", [])).toStrictEqual({})
    const metricWithRemovedIssue = { metric_uuid: { status: "target_met", issue_ids: [] } }
    expect(visibleMetrics(metricWithRemovedIssue, "no_action_required", [])).toStrictEqual({})
    expect(visibleMetrics(metricWithRemovedIssue, "no_issues", [])).toStrictEqual({})
    expect(visibleMetrics(metricWithRemovedIssue, "none", [])).toStrictEqual(metricWithRemovedIssue)
    expect(visibleMetrics(metricWithRemovedIssue, "all", [])).toStrictEqual({})
})

it("hides metrics with hidden tags", () => {
    expect(visibleMetrics({}, false, [])).toStrictEqual({})
    expect(visibleMetrics({}, false, ["hidden"])).toStrictEqual({})
    const metricWithoutTags = { metric_uuid: { tags: [] } }
    expect(visibleMetrics(metricWithoutTags, false, [])).toStrictEqual(metricWithoutTags)
    expect(visibleMetrics(metricWithoutTags, false, ["hidden"])).toStrictEqual({})
    const metricWithHiddenTag = { metric_uuid: { tags: ["hidden"] } }
    expect(visibleMetrics(metricWithHiddenTag, false, [])).toStrictEqual(metricWithHiddenTag)
    expect(visibleMetrics(metricWithHiddenTag, false, ["hidden"])).toStrictEqual({})
    const metricWithMultipleTags = { metric_uuid: { tags: ["hidden", "maybe hidden"] } }
    expect(visibleMetrics(metricWithMultipleTags, false, [])).toStrictEqual(metricWithMultipleTags)
    expect(visibleMetrics(metricWithMultipleTags, false, ["hidden"])).toStrictEqual(metricWithMultipleTags)
    expect(visibleMetrics(metricWithMultipleTags, false, ["hidden", "maybe hidden"])).toStrictEqual({})
})

it("sorts strings with locale compare", () => {
    const strings = ["b", "a", "c"]
    sortWithLocaleCompare(strings)
    expect(strings).toStrictEqual(["a", "b", "c"])
    const emptyArray = []
    sortWithLocaleCompare(emptyArray)
    expect(emptyArray).toStrictEqual([])
})

it("gets the number of reports in a report", () => {
    expect(nrMetricsInReport({ subjects: {} })).toBe(0)
    expect(nrMetricsInReport({ subjects: { subject_uuid: { metrics: {} } } })).toBe(0)
    expect(nrMetricsInReport({ subjects: { subject_uuid: { metrics: { metric_uuid: {} } } } })).toBe(1)
})

it("gets the number of reports in reports", () => {
    expect(nrMetricsInReports([{ subjects: {} }])).toBe(0)
    expect(nrMetricsInReports([{ subjects: { subject_uuid: { metrics: { metric_uuid: {} } } } }])).toBe(1)
})

it("adds counts", () => {
    expect(addCounts({}, {})).toStrictEqual({})
    expect(addCounts({ red: 1 }, { red: 0 })).toStrictEqual({ red: 1 })
    expect(addCounts({ red: 1, green: 3 }, { red: 2, green: 3 })).toStrictEqual({ red: 3, green: 6 })
    expect(() => addCounts({}, { red: 1 })).toThrow()
})

it("sums numbers", () => {
    const array = new Array()
    expect(sum(array)).toBe(0)
    array.push(1)
    expect(sum(array)).toBe(1)
    array.push(2)
    expect(sum(array)).toBe(3)
    expect(sum([])).toBe(0)
    expect(sum([1])).toBe(1)
    expect(sum([1, 2])).toBe(3)
    expect(sum({})).toBe(0)
    expect(sum({ a: 1 })).toBe(1)
    expect(sum({ a: 1, b: 2 })).toBe(3)
})

it("returns whether a measurement is requested for the metric", () => {
    expect(isMeasurementRequested({})).toBe(false)
    expect(isMeasurementRequested({ measurement_requested: "2000-01-01" })).toBe(true)
    const latest = { end: "2024-01-01" }
    expect(isMeasurementRequested({ measurement_requested: "2023-01-01", latest_measurement: latest })).toBe(false)
    expect(isMeasurementRequested({ measurement_requested: "2025-01-01", latest_measurement: latest })).toBe(true)
})
