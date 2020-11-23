import { api_with_report_date, api_version, fetch_server_api } from "./fetch_server_api";

export const nr_measurements_api = `/api/${api_version}/nr_measurements`;

export function get_measurements(metric_uuid, date) {
    return fetch_server_api('get', api_with_report_date(`measurements/${metric_uuid}`, date))
}
