// The default desired response times, as included in the data model configuration by the API-server.
export const desiredResponseTimes = {
    debt_target_met: 60,
    near_target_met: 21,
    target_not_met: 7,
    unknown: 3,
    confirmed: 180,
    false_positive: 180,
    wont_fix: 180,
    fixed: 7,
}

export const dataModel = {
    config: { desired_response_times: desiredResponseTimes },
    subjects: {
        subject_type: { name: "Subject type", metrics: ["metric_type"] },
    },
    metrics: {
        metric_type: {
            name: "Metric type",
            tags: [],
            sources: ["source_type", "source_type_without_location_parameters"],
        },
        metric_type2: {
            name: "Metric type 2",
            description: "Metric type description",
            rationale: "Metric type rationale",
            tags: [],
            sources: ["source_type_without_location_parameters"],
        },
    },
    sources: {
        source_type: {
            name: "Source type name",
            parameters: { url: { type: "url", name: "URL" } },
        },
        source_type_without_location_parameters: {
            name: "Source type without location parameters",
            parameters: {},
        },
    },
}

// A minimal data model with a single metric type that has a count scale.
export const dataModelWithCountScale = {
    config: { desired_response_times: desiredResponseTimes },
    metrics: {
        metric_type: { default_scale: "count" },
    },
}

// A minimal data model with a single metric type and a source type without parameters.
export const dataModelWithSource = {
    metrics: { metric_type: { sources: ["source_type"] } },
    sources: { source_type: { parameters: {} } },
}

export const report = {
    report_uuid: "report_uuid",
    subjects: {
        subject_uuid: {
            type: "subject_type",
            name: "Subject 1 title",
            metrics: {
                metric_uuid: {
                    name: "M1",
                    type: "metric_type",
                    tags: ["other tag"],
                    target: "1",
                    sources: {
                        source_uuid: {
                            name: "Source",
                            type: "source_type",
                            parameters: { url: "https://source1.org" },
                        },
                    },
                    status: "target_not_met",
                    recent_measurements: [],
                    latest_measurement: { count: 1 },
                    comment: "Comment 1",
                },
                metric_uuid2: {
                    name: "M2",
                    type: "metric_type",
                    tags: ["tag"],
                    target: "2",
                    issue_ids: ["ABC-42"],
                    sources: {
                        source_uuid2: {
                            name: "Source 2",
                            type: "source_type",
                            parameters: { url: "https://source2.org" },
                        },
                    },
                    status: "informative",
                    recent_measurements: [],
                    latest_measurement: { count: 2 },
                    comment: "Comment 2",
                },
            },
        },
        subject_uuid2: {
            type: "subject_type",
            name: "Subject 2 title",
            metrics: {
                metric_uuid3: {
                    name: "M3",
                    type: "metric_type",
                    tags: [],
                    sources: {},
                    recent_measurements: [],
                },
            },
        },
    },
    title: "Report title",
}
