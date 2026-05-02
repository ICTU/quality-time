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

export function createNrMeasurementsEventSource({ onInit, onDelta, onError }) {
    const source = new EventSource(nrMeasurementsApi)
    source.addEventListener("init", (message) => onInit(Number(message.data)))
    source.addEventListener("delta", (message) => onDelta(Number(message.data)))
    source.addEventListener("error", () => onError())
    return source
}
