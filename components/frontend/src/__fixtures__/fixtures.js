export const datamodel = {
    subjects: {
      subject_type: { name: "Subject type", metrics: ["metric_type"] }
    },
    metrics: {
      metric_type: { name: "Metric type", tags: [] }
    }
}

export const report = {
    subjects: {
      subject_uuid: {
        type: "subject_type", name: "Subject 1 title", metrics: {
          metric_uuid: {
            name: "M1", type: "metric_type", tags: [], sources: {}, recent_measurements: []
          },
          metric_uuidi2: {
            name: "M2", type: "metric_type", tags: [], sources: {}, recent_measurements: []
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
  };