import { apiWithReportDate, fetchServerApi } from "./fetch_server_api"

export const nrMeasurementsApi = `/api/internal/nr_measurements`

export function getMetricMeasurements(metricUuid, date) {
    return fetchServerApi("get", apiWithReportDate(`measurements/${metricUuid}`, date))
}

export function getMeasurements(minDate, maxDate) {
    const api = apiWithReportDate("measurements", maxDate)
    const sep = api.includes("?") ? "&" : "?"
    return fetchServerApi("get", api + `${sep}min_report_date=${minDate.toISOString()}`)
}
