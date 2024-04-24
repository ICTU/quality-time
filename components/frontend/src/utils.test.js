import { EDIT_ENTITY_PERMISSION, EDIT_REPORT_PERMISSION } from "./context/Permissions"
import {
    capitalize,
    get_metric_target,
    get_source_name,
    get_subject_name,
    getMetricResponseOverrun,
    getMetricTags,
    getReportTags,
    getStatusName,
    getUserPermissions,
    nice_number,
    nrMetricsInReport,
    nrMetricsInReports,
    scaled_number,
    sortWithLocaleCompare,
    sum,
    userPrefersDarkMode,
    visibleMetrics,
} from "./utils"

let matchMediaMatches

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

beforeAll(() => {
    Object.defineProperty(window, "matchMedia", {
        value: jest.fn().mockImplementation((_query) => ({
            matches: matchMediaMatches,
        })),
    })
})

it("capitalizes strings", () => {
    expect(capitalize("")).toBe("")
    expect(capitalize("A")).toBe("A")
    expect(capitalize("a")).toBe("A")
    expect(capitalize("ab")).toBe("Ab")
    expect(capitalize("aB")).toBe("AB")
    expect(capitalize("AB")).toBe("AB")
})

it("rounds numbers nicely", () => {
    expect(nice_number(0)).toBe(10)
    expect(nice_number(1)).toBe(10)
    expect(nice_number(9)).toBe(10)
    expect(nice_number(10)).toBe(12)
    expect(nice_number(12)).toBe(15)
    expect(nice_number(15)).toBe(20)
    expect(nice_number(16)).toBe(20)
    expect(nice_number(17)).toBe(20)
    expect(nice_number(39)).toBe(50)
    expect(nice_number(40)).toBe(50)
    expect(nice_number(41)).toBe(50)
    expect(nice_number(79)).toBe(100)
    expect(nice_number(80)).toBe(100)
    expect(nice_number(81)).toBe(100)
    expect(nice_number(90)).toBe(100)
    expect(nice_number(100)).toBe(120)
    expect(nice_number(125)).toBe(150)
})

it("adds a scale", () => {
    expect(scaled_number(1)).toBe("1")
    expect(scaled_number(12)).toBe("12")
    expect(scaled_number(123)).toBe("123")
    expect(scaled_number(1234)).toBe("1k")
    expect(scaled_number(12345)).toBe("12k")
    expect(scaled_number(123456)).toBe("123k")
    expect(scaled_number(1234567)).toBe("1m")
    expect(scaled_number(12345678)).toBe("12m")
    expect(scaled_number(123456789)).toBe("123m")
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
    expect(get_metric_target({ target: "2" })).toStrictEqual("2")
})

it("gets the metric target, even if the target is missing", () => {
    expect(get_metric_target({})).toStrictEqual("0")
})

it("gets the source name", () => {
    expect(get_source_name({ name: "source" }, {})).toStrictEqual("source")
})

it("gets the source name from the data model if the source has no name", () => {
    expect(get_source_name({ type: "source_type" }, { sources: { source_type: { name: "source" } } })).toStrictEqual(
        "source",
    )
})

it("gets the subject name", () => {
    expect(get_subject_name({ name: "subject" }, {})).toStrictEqual("subject")
})

it("gets the subject name from the data model if the subject has no name", () => {
    expect(
        get_subject_name({ type: "subject_type" }, { subjects: { subject_type: { name: "subject" } } }),
    ).toStrictEqual("subject")
})

it("returns true when the user sets dark mode", () => {
    expect(userPrefersDarkMode("dark")).toBe(true)
})

it("returns false when the user sets light mode", () => {
    expect(userPrefersDarkMode("light")).toBe(false)
})

it("returns true when the user prefers dark mode", () => {
    matchMediaMatches = true
    expect(userPrefersDarkMode("follow_os")).toBe(true)
})

it("returns false when the user prefers light mode", () => {
    matchMediaMatches = false
    expect(userPrefersDarkMode("follow_os")).toBe(false)
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

it("returns the metric response overrun when there is one long measurement and the report has desired response times", () => {
    const report = { desired_response_times: { unknown: 10 } }
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
    expect(visibleMetrics({}, "no_action_needed", [])).toStrictEqual({})
    expect(visibleMetrics({}, "no_issues", [])).toStrictEqual({})
    expect(visibleMetrics({}, "all", [])).toStrictEqual({})
    expect(visibleMetrics({}, "none", [])).toStrictEqual({})
    const metricNotRequiringAction = { metric_uuid: { status: "informative" } }
    expect(visibleMetrics(metricNotRequiringAction, "no_action_needed", [])).toStrictEqual({})
    expect(visibleMetrics(metricNotRequiringAction, "no_issues", [])).toStrictEqual({})
    expect(visibleMetrics(metricNotRequiringAction, "all", [])).toStrictEqual({})
    expect(visibleMetrics(metricNotRequiringAction, "none", [])).toStrictEqual(metricNotRequiringAction)
    const metricRequiringAction = { metric_uuid: { status: "target_not_met" } }
    expect(visibleMetrics(metricRequiringAction, "no_action_needed", [])).toStrictEqual(metricRequiringAction)
    expect(visibleMetrics(metricRequiringAction, "no_issues", [])).toStrictEqual({})
    expect(visibleMetrics(metricRequiringAction, "none", [])).toStrictEqual(metricRequiringAction)
    expect(visibleMetrics(metricRequiringAction, "all", [])).toStrictEqual({})
    const metricWithIssue = { metric_uuid: { status: "target_met", issue_ids: ["ID-1"] } }
    expect(visibleMetrics(metricWithIssue, "no_action_needed", [])).toStrictEqual({})
    expect(visibleMetrics(metricWithIssue, "no_issues", [])).toStrictEqual(metricWithIssue)
    expect(visibleMetrics(metricWithIssue, "none", [])).toStrictEqual(metricWithIssue)
    expect(visibleMetrics(metricWithIssue, "all", [])).toStrictEqual({})
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

it("gets the status name", () => {
    expect(getStatusName("target_met")).toBe("Target met")
    expect(getStatusName("near_target_met")).toBe("Near target met")
    expect(getStatusName("debt_target_met")).toBe("Debt target met")
    expect(getStatusName("target_not_met")).toBe("Target not met")
    expect(getStatusName("informative")).toBe("Informative")
    expect(getStatusName("unknown")).toBe("Unknown")
    expect(getStatusName("")).toBe("Unknown")
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
