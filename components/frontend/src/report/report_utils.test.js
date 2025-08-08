import { summarizeMetricsOnDate } from "./report_utils"

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

function metrics(extra) {
    const metrics = {
        metric_uuid: { type: "metric_type" },
    }
    if (extra) {
        metrics["metric_uuid2"] = { type: "metric_type" }
    }
    return metrics
}

const date = new Date("2025-08-08T11:00:00")

it("summarizes no metrics", () => {
    expect(summarizeMetricsOnDate(dataModel, date, [], {})).toEqual(status())
})

it("summarizes one metric without measurements", () => {
    expect(summarizeMetricsOnDate(dataModel, new Date(), [], metrics())).toEqual(status({ white: 1 }))
})

it("summarizes one metric with one green measurement", () => {
    expect(summarizeMetricsOnDate(dataModel, date, [measurement()], metrics())).toEqual(status({ green: 1 }))
})

it("summarizes one metric with one red measurement", () => {
    expect(
        summarizeMetricsOnDate(dataModel, date, [measurement({ count: { status: "target_not_met" } })], metrics()),
    ).toEqual(status({ red: 1 }))
})

it("summarizes one metric with two measurements", () => {
    expect(
        summarizeMetricsOnDate(
            dataModel,
            date,
            [
                measurement({ count: { status: "informative" } }),
                measurement({ metric_uuid: "metric_uuid2", count: { status: "near_target_met" } }),
            ],
            metrics(true),
        ),
    ).toEqual(status({ blue: 1, yellow: 1 }))
})

it("summarizes one metric with one measurement without status", () => {
    expect(summarizeMetricsOnDate(dataModel, date, [measurement({ count: {} })], metrics())).toEqual(
        status({ white: 1 }),
    )
})

it("summarizes one metric with one measurement without scale", () => {
    expect(summarizeMetricsOnDate(dataModel, date, [measurement({ count: null })], metrics())).toEqual(
        status({ white: 1 }),
    )
})
