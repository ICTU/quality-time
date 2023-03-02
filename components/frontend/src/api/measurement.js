import { api_with_report_date, api_version, fetch_server_api } from "./fetch_server_api";

export const nr_measurements_api = `/api/${api_version}/nr_measurements`;

export function get_metric_measurements(metric_uuid, date) {
    return fetch_server_api('get', api_with_report_date(`measurements/${metric_uuid}`, date))
}

export function get_measurements(date, minDate) {
    const minReportDate = minDate.toISOString().split("T")[0] + "T00:00:00.000Z"; // Ignore the time so we get all measurements for the min date
    const api = api_with_report_date("measurements", date);
    const sep = api.indexOf("?") < 0 ? "?" : "&";
    return fetch_server_api('get', api + `${sep}min_report_date=${minReportDate}`);
}
