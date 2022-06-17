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
    summary_by_subject: {},
    summary_by_tag: {},
    subjects: {
        subject_uuid: {
            type: "subject_type", name: "Subject 1 title", metrics: {
                metric_uuid: {
                    name: "M1", type: "metric_type", tags: [], sources: {}, status: "informative", recent_measurements: []
                },
                metric_uuidi2: {
                    name: "M2", type: "metric_type", tags: ["tag"], issue_ids: ["ABC-42"], sources: {source_uuid: {name: "Source"}}, recent_measurements: []
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
