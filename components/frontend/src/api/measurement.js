import { fetch_server_api } from "./fetch_server_api";

export function get_measurements(metric_uuid, date) {
    return fetch_server_api('get', `measurements/${metric_uuid}?report_date=${date.toISOString()}`, {})
}
