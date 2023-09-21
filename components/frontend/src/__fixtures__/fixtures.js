export const datamodel = {
    subjects: {
        subject_type: { name: "Subject type", metrics: ["metric_type"] }
    },
    metrics: {
        metric_type: { name: "Metric type", tags: [] }
    }
}

export const report = {
    report_uuid: "report_uuid",
    subjects: {
        subject_uuid: {
            type: "subject_type", name: "Subject 1 title", metrics: {
                metric_uuid: {
                    name: "M1",
                    type: "metric_type",
                    tags: ["other tag"],
                    target: "1",
                    sources: {},
                    status: "target_not_met",
                    recent_measurements: [],
                    latest_measurement: {count: 1},
                    comment: "Comment 1"
                },
                metric_uuid2: {
                    name: "M2",
                    type: "metric_type",
                    tags: ["tag"],
                    target: "2",
                    issue_ids: ["ABC-42"],
                    sources: {source_uuid: {name: "Source"}},
                    status: "informative",
                    recent_measurements: [],
                    latest_measurement: {count: 2},
                    comment: "Comment 2"
                }
            }
        },
        subject_uuid2: {
            type: "subject_type", name: "Subject 2 title", metrics: {
                metric_uuid3: {
                    name: "M3", type: "metric_type", tags: [], sources: {}, recent_measurements: []
                }
            }
        }
    }
}
