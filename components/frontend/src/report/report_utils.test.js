import { isLatestDate, metricValueAndStatusOnDate, summarizeMetricsOnDate } from "./report_utils"

function status({ blue = 0, green = 0, grey = 0, red = 0, white = 0, yellow = 0 } = {}) {
    return {
        blue: blue,
        green: green,
        grey: grey,
        red: red,
        white: white,
        yellow: yellow,
    }
}

function measurement({ metric_uuid = "metric_uuid", count = { status: "target_met" } } = {}) {
    const measurement = {
        metric_uuid: metric_uuid,
        start: "2025-08-08T10:00:00",
        end: "2025-08-08T12:00:00",
    }
    if (count !== null) {
        measurement.count = count
    }
    return measurement
}

const dataModel = { metrics: { metric_type: {} } }

function metrics(extra, metric = {}) {
    const metrics = {
        metric_uuid: { type: "metric_type", ...metric },
    }
    if (extra) {
        metrics["metric_uuid2"] = { type: "metric_type" }
    }
    return metrics
}

const date = new Date("2025-08-08T11:00:00")

it("summarizes no metrics", () => {
    expect(summarizeMetricsOnDate(dataModel, date, false, [], {})).toEqual(status())
})

it("summarizes one metric without measurements", () => {
    expect(summarizeMetricsOnDate(dataModel, new Date(), false, [], metrics())).toEqual(status({ white: 1 }))
})

it("summarizes one metric with one green measurement", () => {
    expect(summarizeMetricsOnDate(dataModel, date, false, [measurement()], metrics())).toEqual(status({ green: 1 }))
})

it("summarizes one metric with one red measurement", () => {
    expect(
        summarizeMetricsOnDate(
            dataModel,
            date,
            false,
            [measurement({ count: { status: "target_not_met" } })],
            metrics(),
        ),
    ).toEqual(status({ red: 1 }))
})

it("summarizes one metric with two measurements", () => {
    expect(
        summarizeMetricsOnDate(
            dataModel,
            date,
            false,
            [
                measurement({ count: { status: "informative" } }),
                measurement({ metric_uuid: "metric_uuid2", count: { status: "near_target_met" } }),
            ],
            metrics(true),
        ),
    ).toEqual(status({ blue: 1, yellow: 1 }))
})

it("summarizes one metric with one measurement without status", () => {
    expect(summarizeMetricsOnDate(dataModel, date, false, [measurement({ count: {} })], metrics())).toEqual(
        status({ white: 1 }),
    )
})

it("summarizes one metric with one measurement without scale", () => {
    expect(summarizeMetricsOnDate(dataModel, date, false, [measurement({ count: null })], metrics())).toEqual(
        status({ white: 1 }),
    )
})

it("summarizes one metric on the latest date using the metric status", () => {
    const metric = { status: "target_not_met", latest_measurement: { count: { status: "target_not_met" } } }
    expect(summarizeMetricsOnDate(dataModel, date, true, [measurement()], metrics(false, metric))).toEqual(
        status({ red: 1 }),
    )
})

it("summarizes one metric on the latest date using the metric status if there is no measurement on that date", () => {
    const metric = { status: "target_not_met", latest_measurement: { count: { status: "target_not_met" } } }
    const latestDate = new Date("2025-08-10T11:00:00")
    expect(summarizeMetricsOnDate(dataModel, latestDate, true, [measurement()], metrics(false, metric))).toEqual(
        status({ red: 1 }),
    )
})

it("summarizes one metric with accepted technical debt but without measurements on the latest date", () => {
    expect(summarizeMetricsOnDate(dataModel, date, true, [], metrics(false, { status: "debt_target_met" }))).toEqual(
        status({ grey: 1 }),
    )
})

it("summarizes one metric without status on the latest date", () => {
    expect(summarizeMetricsOnDate(dataModel, date, true, [measurement()], metrics())).toEqual(status({ white: 1 }))
})

it("determines whether a date is the latest date", () => {
    const dates = [new Date("2025-08-06"), new Date("2025-08-08"), new Date("2025-08-07")]
    expect(dates.map((d) => isLatestDate(d, dates))).toEqual([false, true, false])
})

it("returns the value and status of the measurement on the date", () => {
    const metric = { type: "metric_type", status: "target_not_met", latest_measurement: { count: { value: "1" } } }
    const measurements = [measurement({ count: { value: "0", status: "target_met" } })]
    expect(metricValueAndStatusOnDate(dataModel, metric, "metric_uuid", measurements, date, false)).toEqual([
        "0",
        "target_met",
    ])
})

it("returns the value and status of the latest measurement on the latest date", () => {
    const metric = { type: "metric_type", status: "target_not_met", latest_measurement: { count: { value: "1" } } }
    const measurements = [measurement({ count: { value: "0", status: "target_met" } })]
    expect(metricValueAndStatusOnDate(dataModel, metric, "metric_uuid", measurements, date, true)).toEqual([
        "1",
        "target_not_met",
    ])
})

it("returns an unknown value and status on the latest date if the metric has no measurements", () => {
    const metric = { type: "metric_type" }
    expect(metricValueAndStatusOnDate(dataModel, metric, "metric_uuid", [], date, true)).toEqual(["?", "unknown"])
})
