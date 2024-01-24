import { api_with_report_date, api_version, fetch_server_api } from "./fetch_server_api";

export const nr_measurements_api = `/api/${api_version}/nr_measurements`;

export function get_metric_measurements(metric_uuid, date) {
    return fetch_server_api('get', api_with_report_date(`measurements/${metric_uuid}`, date))
}

export function get_measurements(minDate, maxDate) {
    const api = api_with_report_date("measurements", maxDate);
    const sep = api.indexOf("?") < 0 ? "?" : "&";
    return fetch_server_api('get', api + `${sep}min_report_date=${minDate.toISOString()}`);
}
