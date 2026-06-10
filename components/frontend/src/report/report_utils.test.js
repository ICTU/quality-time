import { dataModel as fixtureDataModel, report as fixtureReport } from "../__fixtures__/fixtures"
import {
    metricsUsingSourceLocation,
    sortedSourceLocations,
    sourcesUsingSourceLocation,
    summarizeMetricsOnDate,
    unusedMetricTypesSupportedBySourceLocation,
} from "./report_utils"

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

describe("sortedSourceLocations", () => {
    it("returns an empty list when the report has no source locations", () => {
        expect(sortedSourceLocations(fixtureDataModel, {})).toStrictEqual([])
    })

    it("returns the source locations of the report", () => {
        expect(sortedSourceLocations(fixtureDataModel, fixtureReport)).toStrictEqual([
            ["source_location_uuid", fixtureReport.source_locations.source_location_uuid],
        ])
    })

    it("returns the source locations sorted by source location name", () => {
        const report = {
            source_locations: {
                uuid_b: { location_name: "B location", source_type: "source_type" },
                uuid_c: { source_type: "source_type" }, // Sorts by the source type name, "Source type name"
                uuid_a: { location_name: "A location", source_type: "source_type" },
            },
        }
        expect(sortedSourceLocations(fixtureDataModel, report).map(([uuid]) => uuid)).toStrictEqual([
            "uuid_a",
            "uuid_b",
            "uuid_c",
        ])
    })
})

describe("sourcesUsingSourceLocation", () => {
    it("returns the number of sources that use the source location", () => {
        expect(sourcesUsingSourceLocation(fixtureReport, "source_location_uuid")).toBe(2)
    })

    it("returns zero when no sources use the source location", () => {
        expect(sourcesUsingSourceLocation(fixtureReport, "unused_source_location_uuid")).toBe(0)
    })

    it("returns zero when the report has no subjects", () => {
        expect(sourcesUsingSourceLocation({}, "source_location_uuid")).toBe(0)
    })
})

describe("metricsUsingSourceLocation", () => {
    it("returns the metrics that have a source that uses the source location", () => {
        const metrics = metricsUsingSourceLocation(fixtureDataModel, fixtureReport, "source_location_uuid")
        expect(Object.keys(metrics)).toStrictEqual(["metric_uuid", "metric_uuid2"])
        expect(metrics.metric_uuid).toStrictEqual({
            name: "M1",
            secondary_name: "",
            subjectName: "Subject 1 title",
            subjectUuid: "subject_uuid",
        })
    })

    it("returns no metrics when no sources use the source location", () => {
        expect(
            metricsUsingSourceLocation(fixtureDataModel, fixtureReport, "unused_source_location_uuid"),
        ).toStrictEqual({})
    })
})

describe("unusedMetricTypesSupportedBySourceLocation", () => {
    it("returns the empty set when all supported metric types are used", () => {
        expect(
            unusedMetricTypesSupportedBySourceLocation(fixtureDataModel, fixtureReport, "source_location_uuid"),
        ).toStrictEqual(new Set())
    })

    it("returns all supported metric types when the source location is unused", () => {
        const report = {
            source_locations: {
                source_location_uuid: { source_type: "source_type_without_location_parameters" },
            },
            subjects: {},
        }
        expect(
            unusedMetricTypesSupportedBySourceLocation(fixtureDataModel, report, "source_location_uuid"),
        ).toStrictEqual(new Set(["metric_type", "metric_type2"]))
    })

    it("returns the supported metric types that are not used", () => {
        const report = {
            source_locations: {
                source_location_uuid: { source_type: "source_type_without_location_parameters" },
            },
            subjects: {
                subject_uuid: {
                    metrics: {
                        metric_uuid: {
                            type: "metric_type",
                            sources: {
                                source_uuid: {
                                    type: "source_type_without_location_parameters",
                                    source_location: "source_location_uuid",
                                },
                            },
                        },
                    },
                },
            },
        }
        expect(
            unusedMetricTypesSupportedBySourceLocation(fixtureDataModel, report, "source_location_uuid"),
        ).toStrictEqual(new Set(["metric_type2"]))
    })
})
